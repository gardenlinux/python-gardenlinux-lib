import functools
import logging
import sys
import time

from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def retry_on_error(
    max_retries=3,
    initial_delay=1,
    backoff_factor=2,
    # retry on:
    #   - 502 - bad gateway
    #   - 503 - service unavailable
    #   - 504 - gateway timeout
    #   - 429 - too many requests
    #   - 400 - bad request (e.g. invalid range start for blob upload)
    #   - 404 - not found (e.g. blob not found is seen in unit tests)
    retryable_status_codes=(502, 503, 504, 429, 400, 404),
    retryable_exceptions=(RequestException,),
):
    """
    A decorator for retrying functions that might fail due to transient network issues.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        retryable_status_codes: HTTP status codes that trigger a retry
        retryable_exceptions: Exception types that trigger a retry

    Returns:
        Decorated function with retry logic
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for retry_count in range(max_retries + 1):
                try:
                    if retry_count > 0:
                        logger.info(
                            f"Retry attempt {retry_count}/{max_retries} for {func.__name__}"
                        )

                    response = func(*args, **kwargs)

                    # Check for retryable status codes in the response
                    if (
                        hasattr(response, "status_code")
                        and response.status_code in retryable_status_codes
                    ):
                        status_code = response.status_code
                        logger.warning(
                            f"Received status code {status_code} from {func.__name__}, retrying..."
                        )
                        last_exception = HTTPError(f"HTTP Error {status_code}")
                    else:
                        # Success, return the response
                        return response

                except retryable_exceptions as e:
                    logger.warning(f"Request failed in {func.__name__}: {str(e)}")
                    last_exception = e

                # Don't sleep if this was the last attempt
                if retry_count < max_retries:
                    sleep_time = delay * (backoff_factor**retry_count)
                    logger.info(f"Waiting {sleep_time:.2f} seconds before retry")
                    time.sleep(sleep_time)

            # If we got here, all retries failed
            logger.error(f"All {max_retries} retries failed for {func.__name__}")
            if last_exception:
                raise last_exception
            return None

        return wrapper

    return decorator

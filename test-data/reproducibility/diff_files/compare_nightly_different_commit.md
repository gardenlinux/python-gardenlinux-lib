# Reproducibility Test Results

⚠️ **95.1%** of **81** tested flavors were reproducible.
**1** Problem detected.

## Detailed Result

Comparison of nightly **[#2405](https://github.com/gardenlinux/gardenlinux/actions/runs/19008197684)** and **[#2404](https://github.com/gardenlinux/gardenlinux/actions/runs/18992390789)**

⚠️ The nightlies used different commits: `22b5708` (#2405) != `22b5707` (#2404)

<details><summary>📃 These flavors only passed due to the nightly whitelist</summary><pre>aws-gardener_fips_prod-amd64<br>aws-gardener_fips_prod-arm64<br>aws-gardener_prod_tpm2_trustedboot-amd64<br>aws-gardener_prod_tpm2_trustedboot-arm64</pre></details>

*The mentioned features are included in every affected flavor and not included in every unaffected flavor.*

| Affected Files | Flavors | Features Causing the Problem |
|----------------|---------|------------------------------|
|`/etc/hostname`|**4.9%** affected<br>`container-amd64`<br>`container-arm64`<br>`container-pythonDev-amd64`<br>`container-pythonDev-arm64`|<pre>container</pre>|
|✅ No problems found|**95.1%**<br><details><summary>ali-gardener_prod-amd64...</summary>`ali-gardener_prod-amd64`<br>`aws-gardener_fips_prod-amd64`<br>`aws-gardener_fips_prod-arm64`<br>`aws-gardener_prod-amd64`<br>`aws-gardener_prod-arm64`<br>`aws-gardener_prod_tpm2_trustedboot-amd64`<br>`aws-gardener_prod_tpm2_trustedboot-arm64`<br>`aws-gardener_prod_trustedboot-amd64`<br>`aws-gardener_prod_trustedboot-arm64`<br>`aws-gardener_prod_usi-amd64`<br>`aws-gardener_prod_usi-arm64`<br>`azure-gardener_prod-amd64`<br>`azure-gardener_prod-arm64`<br>`azure-gardener_prod_tpm2_trustedboot-amd64`<br>`azure-gardener_prod_tpm2_trustedboot-arm64`<br>`azure-gardener_prod_trustedboot-amd64`<br>`azure-gardener_prod_trustedboot-arm64`<br>`azure-gardener_prod_usi-amd64`<br>`azure-gardener_prod_usi-arm64`<br>`bare-libc-amd64`<br>`bare-libc-arm64`<br>`bare-nodejs-amd64`<br>`bare-nodejs-arm64`<br>`bare-python-amd64`<br>`bare-python-arm64`<br>`bare-sapmachine-amd64`<br>`bare-sapmachine-arm64`<br>`baremetal-capi-amd64`<br>`baremetal-capi-arm64`<br>`baremetal-gardener_prod-amd64`<br>`baremetal-gardener_prod-arm64`<br>`baremetal-gardener_prod_tpm2_trustedboot-amd64`<br>`baremetal-gardener_prod_tpm2_trustedboot-arm64`<br>`baremetal-gardener_prod_trustedboot-amd64`<br>`baremetal-gardener_prod_trustedboot-arm64`<br>`baremetal-gardener_prod_usi-amd64`<br>`baremetal-gardener_prod_usi-arm64`<br>`baremetal-gardener_pxe-amd64`<br>`baremetal-gardener_pxe-arm64`<br>`baremetal-vhost-amd64`<br>`baremetal-vhost-arm64`<br>`baremetal_pxe-amd64`<br>`baremetal_pxe-arm64`<br>`gcp-gardener_prod-amd64`<br>`gcp-gardener_prod-arm64`<br>`gcp-gardener_prod_tpm2_trustedboot-amd64`<br>`gcp-gardener_prod_tpm2_trustedboot-arm64`<br>`gcp-gardener_prod_trustedboot-amd64`<br>`gcp-gardener_prod_trustedboot-arm64`<br>`gcp-gardener_prod_usi-amd64`<br>`gcp-gardener_prod_usi-arm64`<br>`gdch-gardener_prod-amd64`<br>`gdch-gardener_prod-arm64`<br>`kvm-gardener_prod-amd64`<br>`kvm-gardener_prod-arm64`<br>`kvm-gardener_prod_tpm2_trustedboot-amd64`<br>`kvm-gardener_prod_tpm2_trustedboot-arm64`<br>`kvm-gardener_prod_trustedboot-amd64`<br>`kvm-gardener_prod_trustedboot-arm64`<br>`kvm-gardener_prod_usi-amd64`<br>`kvm-gardener_prod_usi-arm64`<br>`lima-amd64`<br>`lima-arm64`<br>`openstack-gardener_prod-amd64`<br>`openstack-gardener_prod-arm64`<br>`openstack-gardener_prod_tpm2_trustedboot-amd64`<br>`openstack-gardener_prod_tpm2_trustedboot-arm64`<br>`openstack-gardener_prod_trustedboot-amd64`<br>`openstack-gardener_prod_trustedboot-arm64`<br>`openstack-gardener_prod_usi-amd64`<br>`openstack-gardener_prod_usi-arm64`<br>`openstack-metal-gardener_prod-amd64`<br>`openstack-metal-gardener_prod-arm64`<br>`openstack-metal-gardener_prod_usi-amd64`<br>`openstack-metal-gardener_prod_usi-arm64`<br>`vmware-gardener_prod-amd64`<br>`vmware-gardener_prod-arm64`</details>|-|

*To add affected files to the whitelist, edit the `whitelist` variable in python-gardenlinux-lib `src/gardenlinux/features/reproducibility/comparator.py`*

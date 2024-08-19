#!/bin/bash


echo "This will take a while. Building for the following targets:"

test_targets=("aws-gardener_prod" "azure-gardener_prod" "gcp-gardener_prod" "openstack-gardener_prod" "openstackbaremetal-gardener_prod" "metal-kvm_dev")
#test_arch=("arm64", "amd64")
test_arch=("amd64")

for target in "${test_targets[@]}"; do
  echo "$target (amd64 and arm64)"
done

read -p "Build targets listed above? (y/n): " confirm
if [[ "$confirm" != [yY] ]]; then
    exit 1
fi

pushd gardenlinux
for target in "${test_targets[@]}"; do
  for arch in "${test_arch[@]}"; do
    ./build "$target-$arch"
  done
done
popd


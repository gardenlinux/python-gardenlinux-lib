#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "This will take a while. Building for the following targets:"

test_targets=(
    "aws-gardener_prod"
    "azure-gardener_prod"
    "gcp-gardener_prod"
    "openstack-gardener_prod"
    "openstackbaremetal-gardener_prod"
    "metal-kvm_dev"
)
test_arch=("amd64")
pushd $script_dir/gardenlinux
commit=$(git rev-parse --short=8 HEAD)
popd
fake_artifacts=(
  "aws-gardener_prod-today-amd64-$commit.raw"
  "aws-gardener_prod-today-arm64-$commit.raw"
  "aws-gardener_prod-today-amd64-$commit.tar"
  "aws-gardener_prod-today-arm64-$commit.tar"
  "gcp-gardener_prod-today-amd64-$commit.tar.gz"
  "gcp-gardener_prod-today-arm64-$commit.tar.gz"
  "gcp-gardener_prod-today-amd64-$commit.gcpimage.tar.gz"
  "gcp-gardener_prod-today-arm64-$commit.gcpimage.tar.gz"
  "azure-gardener_prod-today-amd64-$commit.vhd"
  "azure-gardener_prod-today-arm64-$commit.vhd"
  "azure-gardener_prod-today-amd64-$commit.tar"
  "azure-gardener_prod-today-arm64-$commit.tar"
  "openstack-gardener_prod-today-amd64-$commit.qcow2"
  "openstack-gardener_prod-today-arm64-$commit.qcow2"
  "openstack-gardener_prod-today-amd64-$commit.vmdk"
  "openstack-gardener_prod-today-arm64-$commit.vmdk"
  "openstack-gardener_prod-today-amd64-$commit.tar"
  "openstack-gardener_prod-today-arm64-$commit.tar"
  "openstackbaremetal-gardener_prod-today-amd64-$commit.raw"
  "openstackbaremetal-gardener_prod-today-arm64-$commit.raw"
  "openstackbaremetal-gardener_prod-today-amd64-$commit.tar"
  "openstackbaremetal-gardener_prod-today-arm64-$commit.tar"
  "openstackbaremetal-gardener_prod-today-amd64-$commit.qcow2"
  "openstackbaremetal-gardener_prod-today-arm64-$commit.qcow2"
  "openstackbaremetal-gardener_prod-today-amd64-$commit.vmdk"
  "openstackbaremetal-gardener_prod-today-arm64-$commit.vmdk"
  "metal-kvm_dev-today-amd64-$commit.raw"
  "metal-kvm_dev-today-arm64-$commit.raw"
  "metal-kvm_dev-today-amd64-$commit.tar"
  "metal-kvm_dev-today-arm64-$commit.tar"
  )


# Check if the --dummy flag is set
dummy_mode=false
if [[ "$1" == "--dummy" ]]; then
    dummy_mode=true
    echo "Dummy mode enabled. No actual builds will be performed."
    for target in "${test_targets[@]}"; do
      echo "$target (amd64 and arm64)"
    done
  else
    read -p "Build targets listed above? (y/n): " confirm 
      if [[ "$confirm" != [yY] ]]; then
        exit 1
    fi
fi



if [ "$dummy_mode" = true ]; then
    echo "Creating fake artifacts..."
    mkdir -p $script_dir/gardenlinux/.build
    for artifact in "${fake_artifacts[@]}"; do
        echo "Creating fake artifact: $artifact"
        touch "$script_dir/gardenlinux/.build/$artifact"  # This simulates creating a fake artifact file
    done
    echo "Fake artifacts created."
else
    pushd $script_dir/gardenlinux
    for target in "${test_targets[@]}"; do
      for arch in "${test_arch[@]}"; do
        echo "Building $target-$arch..."
        ./build "$target-$arch"
      done
    done
    popd
fi


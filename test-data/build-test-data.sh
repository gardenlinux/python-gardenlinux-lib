#!/usr/bin/env bash
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
  "aws-gardener_prod-amd64-today-$commit.raw"
  "aws-gardener_prod-arm64-today-$commit.raw"
  "aws-gardener_prod-amd64-today-$commit.tar"
  "aws-gardener_prod-arm64-today-$commit.tar"
  "gcp-gardener_prod-amd64-today-$commit.tar.gz"
  "gcp-gardener_prod-arm64-today-$commit.tar.gz"
  "gcp-gardener_prod-amd64-today-$commit.gcpimage.tar.gz"
  "gcp-gardener_prod-arm64-today-$commit.gcpimage.tar.gz"
  "azure-gardener_prod-amd64-today-$commit.vhd"
  "azure-gardener_prod-arm64-today-$commit.vhd"
  "azure-gardener_prod-amd64-today-$commit.tar"
  "azure-gardener_prod-arm64-today-$commit.tar"
  "openstack-gardener_prod-amd64-today-$commit.qcow2"
  "openstack-gardener_prod-arm64-today-$commit.qcow2"
  "openstack-gardener_prod-amd64-today-$commit.vmdk"
  "openstack-gardener_prod-arm64-today-$commit.vmdk"
  "openstack-gardener_prod-amd64-today-$commit.tar"
  "openstack-gardener_prod-arm64-today-$commit.tar"
  "openstackbaremetal-gardener_prod-amd64-today-$commit.raw"
  "openstackbaremetal-gardener_prod-arm64-today-$commit.raw"
  "openstackbaremetal-gardener_prod-amd64-today-$commit.tar"
  "openstackbaremetal-gardener_prod-arm64-today-$commit.tar"
  "openstackbaremetal-gardener_prod-amd64-today-$commit.qcow2"
  "openstackbaremetal-gardener_prod-arm64-today-$commit.qcow2"
  "openstackbaremetal-gardener_prod-amd64-today-$commit.vmdk"
  "openstackbaremetal-gardener_prod-arm64-today-$commit.vmdk"
  "metal-kvm_dev-amd64-today-$commit.raw"
  "metal-kvm_dev-arm64-today-$commit.raw"
  "metal-kvm_dev-amd64-today-$commit.tar"
  "metal-kvm_dev-arm64-today-$commit.tar"
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


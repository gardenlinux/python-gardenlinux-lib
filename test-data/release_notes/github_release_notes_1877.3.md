## Changes
The following packages have been upgraded, to address the mentioned CVEs:
- upgrade 'gnutls28' from `3.8.9-2` to `3.8.9-3gl0+bp1877`
  - CVE-2025-32988
  - CVE-2025-32989
  - CVE-2025-32990
  - CVE-2025-6395
- upgrade 'sqlite3' from `3.46.1-4` to `3.46.1-7gl0+bp1877`
  - CVE-2025-6965
- upgrade 'dpkg' from `1.22.18` to `1.22.21gl0+bp1877`
  - CVE-2025-6297
- upgrade 'linux' from `6.12.40-2gl0` to `6.12.44-3gl0`
  - CVE-2025-38676
  - CVE-2025-38683
  - CVE-2025-38684
  - CVE-2025-38686
  - CVE-2025-38687
  - CVE-2025-38688
  - CVE-2025-38691
  - CVE-2025-38692
  - CVE-2025-38695
  - CVE-2025-38696
  - CVE-2025-38699
  - CVE-2025-38700
  - CVE-2025-38701
  - CVE-2025-38704
  - CVE-2025-38708
  - CVE-2025-38709
  - CVE-2025-38710
  - CVE-2025-38711
  - CVE-2025-38717
  - CVE-2025-38718
  - CVE-2025-38721
  - CVE-2025-38722
  - CVE-2025-38724
  - CVE-2025-38726
  - CVE-2025-38727
  - CVE-2025-38728
  - CVE-2025-38730
  - CVE-2025-38601
  - CVE-2025-38604
  - CVE-2025-38608
  - CVE-2025-38609
  - CVE-2025-38610
  - CVE-2025-38614
  - CVE-2022-50031
  - CVE-2022-50083
  - CVE-2023-53137
  - CVE-2025-37744
  - CVE-2025-38500
  - CVE-2025-38501
  - CVE-2025-38732
  - CVE-2025-38734
  - CVE-2025-38735
  - CVE-2025-38737
  - CVE-2025-39673
  - CVE-2025-39676
  - CVE-2025-39681
  - CVE-2025-39682
  - CVE-2025-39683
  - CVE-2025-39684
  - CVE-2025-39685
  - CVE-2025-39686
  - CVE-2025-39689
  - CVE-2025-39691
  - CVE-2025-39692
  - CVE-2025-39695
  - CVE-2025-39697
  - CVE-2025-39698
  - CVE-2025-39700
  - CVE-2025-39701
  - CVE-2025-39702
  - CVE-2025-39703
  - CVE-2025-39718
  - CVE-2025-39720
  - CVE-2025-39721
  - CVE-2025-39722
  - CVE-2025-39724
  - CVE-2025-39727
  - CVE-2025-39730
  - CVE-2025-39732
  - CVE-2025-21884
  - CVE-2025-38335
  - CVE-2025-38351
  - CVE-2025-38553
  - CVE-2025-38559
  - CVE-2025-38560
  - CVE-2025-38561
  - CVE-2025-38562
  - CVE-2025-38563
  - CVE-2025-38565
  - CVE-2025-38566
  - CVE-2025-38568
  - CVE-2025-38569
  - CVE-2025-38571
  - CVE-2025-38572
  - CVE-2025-38574
  - CVE-2025-38581
  - CVE-2025-38582
  - CVE-2025-38583
  - CVE-2025-38586
  - CVE-2025-38587
  - CVE-2025-38588
  - CVE-2025-38590
  - CVE-2025-38593
  - CVE-2025-38616
  - CVE-2025-38617
  - CVE-2025-38618
  - CVE-2025-38622
  - CVE-2025-38624
  - CVE-2025-38625
  - CVE-2025-38628
  - CVE-2025-38631
  - CVE-2025-38632
  - CVE-2025-38634
  - CVE-2025-38635
  - CVE-2025-38639
  - CVE-2025-38640
  - CVE-2025-38644
  - CVE-2025-38645
  - CVE-2025-38646
  - CVE-2025-38653
  - CVE-2025-38659
  - CVE-2025-38660
  - CVE-2025-38666
  - CVE-2025-38668
  - CVE-2025-38670
  - CVE-2025-38675
  - CVE-2025-39736
  - CVE-2025-39737
  - CVE-2025-39738
  - CVE-2025-39739
  - CVE-2025-39742
  - CVE-2025-39744
  - CVE-2025-39746
  - CVE-2025-39748
  - CVE-2025-39749
  - CVE-2025-39750
  - CVE-2025-39752
  - CVE-2025-39753
  - CVE-2025-39754
  - CVE-2025-39756
  - CVE-2025-39758
  - CVE-2025-39759
  - CVE-2025-39761
  - CVE-2025-39763
  - CVE-2025-39766
  - CVE-2025-39770
  - CVE-2025-39773
  - CVE-2025-39776
  - CVE-2025-39779
  - CVE-2025-39780
  - CVE-2025-39782
  - CVE-2025-39783
  - CVE-2025-39787
  - CVE-2025-39788
  - CVE-2025-39790
  - CVE-2025-39791
- upgrade 'iputils' from `3:20240905-3` to `3:20250605-1gl0~bp1877`
  - CVE-2025-47268

## Software Component Versions
```
containerd 2.1.4-0gl1+bp1877
curl 8.14.1-2gl0+bp1877
libc-bin 2.41-7
linux-image-amd64 6.12.44-3gl0
openssh-server 1:10.0p1-5gl0
openssl 3.5.0-1gl0
runc 1.3.0-1gl0+bp1877
systemd 257.5-2gl0
```

## Changes in Package Versions Compared to 1877.2
| Package | 1877.2 | 1877.3 |
|---------|--------------------|-------------------|
|bpftool | 7.5.0+6.12.40-2gl0 | 7.5.0+6.12.44-3gl0 |
|bpftool-dbgsym | 7.5.0+6.12.40-2gl0 | 7.5.0+6.12.44-3gl0 |
|dpkg | 1.22.18 | 1.22.21gl0+bp1877 |
|dpkg-dbgsym | - | 1.22.21gl0+bp1877 |
|dpkg-dev | 1.22.18 | 1.22.21gl0+bp1877 |
|dselect | - | 1.22.21gl0+bp1877 |
|dselect-dbgsym | - | 1.22.21gl0+bp1877 |
|gnutls-bin | - | 3.8.9-3gl0+bp1877 |
|gnutls-bin-dbgsym | - | 3.8.9-3gl0+bp1877 |
|gnutls-doc | - | 3.8.9-3gl0+bp1877 |
|golang-github-opencontainers-runc-dev | 1.1.15+ds1-2gl1+bp1877 | 1.3.0-1gl0+bp1877 |
|hyperv-daemons | 6.12.40-2gl0 | 6.12.44-3gl0 |
|hyperv-daemons-dbgsym | 6.12.40-2gl0 | 6.12.44-3gl0 |
|intel-sdsi | 6.12.40-2gl0 | 6.12.44-3gl0 |
|intel-sdsi-dbgsym | 6.12.40-2gl0 | 6.12.44-3gl0 |
|iputils-arping | 3:20240905-3 | 3:20250605-1gl0~bp1877 |
|iputils-arping-dbgsym | - | 3:20250605-1gl0~bp1877 |
|iputils-clockdiff | - | 3:20250605-1gl0~bp1877 |
|iputils-clockdiff-dbgsym | - | 3:20250605-1gl0~bp1877 |
|iputils-ping | 3:20240905-3 | 3:20250605-1gl0~bp1877 |
|iputils-ping-dbgsym | - | 3:20250605-1gl0~bp1877 |
|iputils-tracepath | 3:20240905-3 | 3:20250605-1gl0~bp1877 |
|iputils-tracepath-dbgsym | - | 3:20250605-1gl0~bp1877 |
|lemon | - | 3.46.1-7gl0+bp1877 |
|lemon-dbgsym | - | 3.46.1-7gl0+bp1877 |
|libcpupower-dev | 6.12.40-2gl0 | 6.12.44-3gl0 |
|libcpupower1 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|libcpupower1-dbgsym | 6.12.40-2gl0 | 6.12.44-3gl0 |
|libdpkg-dev | - | 1.22.21gl0+bp1877 |
|libdpkg-perl | 1.22.18 | 1.22.21gl0+bp1877 |
|libgnutls-dane0t64 | 3.8.9-2 | 3.8.9-3gl0+bp1877 |
|libgnutls-dane0t64-dbgsym | - | 3.8.9-3gl0+bp1877 |
|libgnutls-openssl27t64 | 3.8.9-2 | 3.8.9-3gl0+bp1877 |
|libgnutls-openssl27t64-dbgsym | - | 3.8.9-3gl0+bp1877 |
|libgnutls28-dev | 3.8.9-2 | 3.8.9-3gl0+bp1877 |
|libgnutls30t64 | 3.8.9-2 | 3.8.9-3gl0+bp1877 |
|libgnutls30t64-dbgsym | - | 3.8.9-3gl0+bp1877 |
|libmd-dev | - | 1.1.0-2+b1 |
|libsqlite3-0 | 3.46.1-4 | 3.46.1-7gl0+bp1877 |
|libsqlite3-0-dbgsym | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-dev | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-ext-csv | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-ext-csv-dbgsym | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-ext-icu | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-ext-icu-dbgsym | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-tcl | - | 3.46.1-7gl0+bp1877 |
|libsqlite3-tcl-dbgsym | - | 3.46.1-7gl0+bp1877 |
|linux-base | 4.11 | 4.12gl0+bp1877 |
|linux-bpf-dev | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-config-6.12 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-cpupower | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-cpupower-dbgsym | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-headers-6.12.40-amd64 | 6.12.40-2gl0 | - |
|linux-headers-6.12.40-cloud-amd64 | 6.12.40-2gl0 | - |
|linux-headers-6.12.40-common | 6.12.40-2gl0 | - |
|linux-headers-6.12.40-firecracker-amd64 | 6.12.40-2gl0 | - |
|linux-headers-6.12.44-amd64 | - | 6.12.44-3gl0 |
|linux-headers-6.12.44-cloud-amd64 | - | 6.12.44-3gl0 |
|linux-headers-6.12.44-common | - | 6.12.44-3gl0 |
|linux-headers-6.12.44-firecracker-amd64 | - | 6.12.44-3gl0 |
|linux-headers-amd64 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-headers-cloud-amd64 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-headers-firecracker-amd64 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-image-6.12.40-amd64 | 6.12.40-2gl0 | - |
|linux-image-6.12.40-amd64-dbg | 6.12.40-2gl0 | - |
|linux-image-6.12.40-cloud-amd64 | 6.12.40-2gl0 | - |
|linux-image-6.12.40-cloud-amd64-dbg | 6.12.40-2gl0 | - |
|linux-image-6.12.40-firecracker-amd64 | 6.12.40-2gl0 | - |
|linux-image-6.12.40-firecracker-amd64-dbg | 6.12.40-2gl0 | - |
|linux-image-6.12.44-amd64 | - | 6.12.44-3gl0 |
|linux-image-6.12.44-amd64-dbg | - | 6.12.44-3gl0 |
|linux-image-6.12.44-cloud-amd64 | - | 6.12.44-3gl0 |
|linux-image-6.12.44-cloud-amd64-dbg | - | 6.12.44-3gl0 |
|linux-image-6.12.44-firecracker-amd64 | - | 6.12.44-3gl0 |
|linux-image-6.12.44-firecracker-amd64-dbg | - | 6.12.44-3gl0 |
|linux-image-amd64 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-image-amd64-dbg | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-image-cloud-amd64 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-image-cloud-amd64-dbg | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-image-firecracker-amd64 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-image-firecracker-amd64-dbg | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-kbuild-6.12.40 | 6.12.40-2gl0 | - |
|linux-kbuild-6.12.40-dbgsym | 6.12.40-2gl0 | - |
|linux-kbuild-6.12.44 | - | 6.12.44-3gl0 |
|linux-kbuild-6.12.44-dbgsym | - | 6.12.44-3gl0 |
|linux-libc-dev | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-source | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-source-6.12 | 6.12.40-2gl0 | 6.12.44-3gl0 |
|linux-support-6.12.40 | 6.12.40-2gl0 | - |
|linux-support-6.12.44 | - | 6.12.44-3gl0 |
|linux-sysctl-defaults | 4.11 | 4.12gl0+bp1877 |
|rtla | 6.12.40-2gl0 | 6.12.44-3gl0 |
|rtla-dbgsym | 6.12.40-2gl0 | 6.12.44-3gl0 |
|runc | 1.1.15+ds1-2gl1+bp1877 | 1.3.0-1gl0+bp1877 |
|runc-dbgsym | 1.1.15+ds1-2gl1+bp1877 | 1.3.0-1gl0+bp1877 |
|sqlite3 | - | 3.46.1-7gl0+bp1877 |
|sqlite3-dbgsym | - | 3.46.1-7gl0+bp1877 |
|sqlite3-doc | - | 3.46.1-7gl0+bp1877 |
|sqlite3-tools | - | 3.46.1-7gl0+bp1877 |
|sqlite3-tools-dbgsym | - | 3.46.1-7gl0+bp1877 |
|usbip | 2.0+6.12.40-2gl0 | 2.0+6.12.44-3gl0 |
|usbip-dbgsym | 2.0+6.12.40-2gl0 | 2.0+6.12.44-3gl0 |
## Published Images

<details>
<summary>📊 Table View</summary>

| Variant | Platform | Architecture | Flavor | Regions & Image IDs | Download Links |
|---------|----------|--------------|--------|---------------------|----------------|
| Default | Alibaba Cloud | amd64 | `ali-gardener_prod-amd64-1877.3-75df9f40` | <details><summary>28 regions</summary><br>**cn-qingdao:** m-m5efm8l2bltkbloui235<br>**cn-beijing:** m-2zee5ebi20ltzy5et7in<br>**cn-zhangjiakou:** m-8vbddy2wfex9nb29afcy<br>**cn-huhehaote:** m-hp3bx14og6cw9thujw1d<br>**cn-wulanchabu:** m-0jlh1iq2f3bryb5okjdk<br>**cn-hangzhou:** m-bp13aseh5a2wn0s5rdz6<br>**cn-shanghai:** m-uf61jbe9n8a9291h4u21<br>**cn-nanjing:** m-gc77bfbctuzphl2bpk0o<br>**cn-shenzhen:** m-wz9gio8m5ey0foj0g4xx<br>**cn-heyuan:** m-f8zdn54v0blnsafxb1t5<br>**cn-guangzhou:** m-7xv0q5feffsxxyttxdy9<br>**cn-fuzhou:** m-gw07bfbctuzphl2bpk0p<br>**cn-wuhan-lr:** m-n4a1u2avlb9pq0u5bdms<br>**cn-chengdu:** m-2vc5saul2saa2z57h216<br>**cn-hongkong:** m-j6c4zk6mwb2673iq5wrz<br>**ap-northeast-1:** m-6weibwo3vrt7ar7nelc9<br>**ap-northeast-2:** m-mj73oldn06th2vy0ymhv<br>**ap-southeast-1:** m-t4ngrf81d0fohwq493pw<br>**ap-southeast-3:** m-8psd64gzc1eru0qld7cc<br>**ap-southeast-6:** m-5tsdd6k3z1vvdyyio7zn<br>**ap-southeast-5:** m-k1aj4usnhqcssa2fpy0c<br>**ap-southeast-7:** m-0jo6uwekvn0gnwhwnq3s<br>**us-east-1:** m-0xi8netpfc2fdwfstz3c<br>**us-west-1:** m-rj9gwpx907qv6p6x8w45<br>**na-south-1:** m-4hfi34x77oaeznwuulq6<br>**eu-west-1:** m-d7o2ny5xc0m3kacxjbem<br>**me-east-1:** m-eb39mgohcec6gaynet9l<br>**eu-central-1:** m-gw86dlqmpaugljiykx91<br></details> | <details><summary>Download</summary><br>[ali-gardener_prod-amd64-1877.3-75df9f40.qcow2](https://gardenlinux-github-releases.s3.amazonaws.com/objects/ali-gardener_prod-amd64-1877.3-75df9f40/ali-gardener_prod-amd64-1877.3-75df9f40.qcow2)</details> |
| Default | Amazon Web Services | amd64 | `aws-gardener_prod-amd64-1877.3-75df9f40` | <details><summary>21 regions</summary><br>**ap-south-1:** ami-00c6adf1de4dd746a<br>**eu-north-1:** ami-07ad3940828172b90<br>**eu-west-3:** ami-071f4f48679d86638<br>**eu-south-1:** ami-0b10af1a19df9f038<br>**eu-west-2:** ami-0e2b7fe07573b71cd<br>**eu-west-1:** ami-01c547eb85d61da61<br>**ap-northeast-3:** ami-0dad917ede94cd3c7<br>**ap-northeast-2:** ami-0ecbeaf40d4643016<br>**ap-northeast-1:** ami-0b7225242babad11c<br>**me-central-1:** ami-0d298e552bf051bc7<br>**ca-central-1:** ami-0af8422162c8f056e<br>**sa-east-1:** ami-05d885175e942fc80<br>**ap-southeast-1:** ami-0a9802680adf7e430<br>**ap-southeast-2:** ami-07ed6f1e62fbd6d66<br>**us-east-1:** ami-055a0ce37433fcdee<br>**us-east-2:** ami-07e9069631850755a<br>**us-west-1:** ami-08c18abab76066f71<br>**us-west-2:** ami-00eca0475f90a1f8c<br>**eu-central-1:** ami-0198822fa7d539f8c<br>**cn-north-1:** ami-093c993faaca89b4d<br>**cn-northwest-1:** ami-05e1cc73d997d67b7<br></details> | <details><summary>Download</summary><br>[aws-gardener_prod-amd64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod-amd64-1877.3-75df9f40/aws-gardener_prod-amd64-1877.3-75df9f40.raw)</details> |
| Default | Amazon Web Services | arm64 | `aws-gardener_prod-arm64-1877.3-75df9f40` | <details><summary>21 regions</summary><br>**ap-south-1:** ami-00cd00c30d19609a2<br>**eu-north-1:** ami-0a969a1a1c4726831<br>**eu-west-3:** ami-0b579f6c70b7c4fe6<br>**eu-south-1:** ami-06c38608e2e7223d3<br>**eu-west-2:** ami-005c7058c3923b2eb<br>**eu-west-1:** ami-0395c3cd38a0a5cd6<br>**ap-northeast-3:** ami-0db3697cea87a5104<br>**ap-northeast-2:** ami-084444f62c7c580fb<br>**ap-northeast-1:** ami-017237dd9abeae8dd<br>**me-central-1:** ami-08efdb3153d0cd184<br>**ca-central-1:** ami-05b535ae9418fee3d<br>**sa-east-1:** ami-036ded98bad763e3c<br>**ap-southeast-1:** ami-03fcefb2fd18519d0<br>**ap-southeast-2:** ami-040f9d0caa5d79e84<br>**us-east-1:** ami-04110d6a1970e748c<br>**us-east-2:** ami-0c8dc664a21d5ca08<br>**us-west-1:** ami-0ddc462d075935666<br>**us-west-2:** ami-0e67c2546e54fed06<br>**eu-central-1:** ami-06a2a1e7da947b192<br>**cn-north-1:** ami-0b3755339496a3158<br>**cn-northwest-1:** ami-06fc0f74b500d2d82<br></details> | <details><summary>Download</summary><br>[aws-gardener_prod-arm64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod-arm64-1877.3-75df9f40/aws-gardener_prod-arm64-1877.3-75df9f40.raw)</details> |
| Default | Microsoft Azure | amd64 | `azure-gardener_prod-amd64-1877.3-75df9f40` | <details><summary>4 gallery + 0 marketplace images</summary><br>**Gallery Images:**<br>• V1 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme/Versions/1877.3.0<br>• V2 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2/Versions/1877.3.0<br>• V1 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme/Versions/1877.3.0<br>• V2 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2/Versions/1877.3.0<br></details> | <details><summary>Download</summary><br>[azure-gardener_prod-amd64-1877.3-75df9f40.vhd](https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod-amd64-1877.3-75df9f40/azure-gardener_prod-amd64-1877.3-75df9f40.vhd)</details> |
| Default | Microsoft Azure | arm64 | `azure-gardener_prod-arm64-1877.3-75df9f40` | <details><summary>2 gallery + 0 marketplace images</summary><br>**Gallery Images:**<br>• V2 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2/Versions/1877.3.0<br>• V2 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2/Versions/1877.3.0<br></details> | <details><summary>Download</summary><br>[azure-gardener_prod-arm64-1877.3-75df9f40.vhd](https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod-arm64-1877.3-75df9f40/azure-gardener_prod-arm64-1877.3-75df9f40.vhd)</details> |
| Default | Google Cloud Platform | amd64 | `gcp-gardener_prod-amd64-1877.3-75df9f40` | <details><summary>Global availability</summary><br>**Image Name:** gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1877-3-75df9f40<br>**Project:** sap-se-gcp-gardenlinux<br>**Availability:** Global (all regions)<br></details> | <details><summary>Download</summary><br>[gcp-gardener_prod-amd64-1877.3-75df9f40.gcpimage.tar.gz](https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod-amd64-1877.3-75df9f40/gcp-gardener_prod-amd64-1877.3-75df9f40.gcpimage.tar.gz)</details> |
| Default | Google Cloud Platform | arm64 | `gcp-gardener_prod-arm64-1877.3-75df9f40` | <details><summary>Global availability</summary><br>**Image Name:** gardenlinux-gcp-c8504d3c3e67cf2fc7c3408c-1877-3-75df9f40<br>**Project:** sap-se-gcp-gardenlinux<br>**Availability:** Global (all regions)<br></details> | <details><summary>Download</summary><br>[gcp-gardener_prod-arm64-1877.3-75df9f40.gcpimage.tar.gz](https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod-arm64-1877.3-75df9f40/gcp-gardener_prod-arm64-1877.3-75df9f40.gcpimage.tar.gz)</details> |
| Default | OpenStack | amd64 | `openstack-gardener_prod-amd64-1877.3-75df9f40` | <details><summary>15 regions</summary><br>**eu-de-1:** ed3b4c3d-941f-456a-a551-bd52b8397443 (gardenlinux-1877.3)<br>**eu-de-2:** 5ea6fb4f-20fc-43b8-8ffe-af8da6d61d6a (gardenlinux-1877.3)<br>**eu-nl-1:** ac9b5d43-ff53-494d-8adf-2249c324a9db (gardenlinux-1877.3)<br>**la-br-1:** 404f22a3-9822-4696-a60f-8566eedb93e3 (gardenlinux-1877.3)<br>**na-ca-1:** b69b72f3-574a-4f76-b4eb-ac9185ea2681 (gardenlinux-1877.3)<br>**na-us-1:** 40e99366-f13b-402a-a264-e7e4773ab8ba (gardenlinux-1877.3)<br>**na-us-2:** c50200c6-95fd-4a97-bef2-90b2d6afa3d3 (gardenlinux-1877.3)<br>**na-us-3:** d5b1d8c0-3420-4a82-931d-0506a6b8f166 (gardenlinux-1877.3)<br>**ap-ae-1:** 81c26cb7-c515-4610-949a-92c275640325 (gardenlinux-1877.3)<br>**ap-au-1:** 2d6e3edd-5596-41e6-a640-4b1b8e7310e7 (gardenlinux-1877.3)<br>**ap-cn-1:** 3564b5ef-9b37-4926-bb23-5655cf90de69 (gardenlinux-1877.3)<br>**ap-jp-1:** 2ff61187-f004-4317-bd4c-a17d93b475bc (gardenlinux-1877.3)<br>**ap-jp-2:** 2bc58951-9bf7-445b-a6e4-f634c7522d9b (gardenlinux-1877.3)<br>**ap-sa-1:** e4a4aa92-335a-454b-83bb-643cb918cf6a (gardenlinux-1877.3)<br>**ap-sa-2:** d3ac5df8-ce38-4a23-b611-dfef6b7a0db9 (gardenlinux-1877.3)<br></details> | <details><summary>Download</summary><br>[openstack-gardener_prod-amd64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/openstack-gardener_prod-amd64-1877.3-75df9f40/openstack-gardener_prod-amd64-1877.3-75df9f40.raw)</details> |
| Default | OpenStack Baremetal | amd64 | `openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40` | <details><summary>15 regions</summary><br>**eu-de-1:** 01c3ab26-5b93-4655-a743-1fef60f64b53 (gardenlinux-1877.3-baremetal)<br>**eu-de-2:** 7488d07b-65f1-4b85-8df8-13244b895d71 (gardenlinux-1877.3-baremetal)<br>**eu-nl-1:** 1926a818-55d5-49e1-9af8-eab8450705eb (gardenlinux-1877.3-baremetal)<br>**la-br-1:** 6fda686d-d2f7-4018-ab4c-1250e898197a (gardenlinux-1877.3-baremetal)<br>**na-ca-1:** a032ecc1-3bee-4d65-9f68-3e3f99e2c291 (gardenlinux-1877.3-baremetal)<br>**na-us-1:** d663d5f1-1b44-41af-9039-e36cc64a5920 (gardenlinux-1877.3-baremetal)<br>**na-us-2:** 818bbfdd-4ee4-49ee-8294-dc3a3c66971f (gardenlinux-1877.3-baremetal)<br>**na-us-3:** b154b48b-050f-48d6-997f-b6c2756079a6 (gardenlinux-1877.3-baremetal)<br>**ap-ae-1:** 5992e19c-2ca2-47be-ae55-50e2fd26b662 (gardenlinux-1877.3-baremetal)<br>**ap-au-1:** 986403a6-e254-4689-8f81-e32dc33c9b64 (gardenlinux-1877.3-baremetal)<br>**ap-cn-1:** 0c794890-a690-4881-b0c2-39a939b020e2 (gardenlinux-1877.3-baremetal)<br>**ap-jp-1:** f5be2c30-8e8e-4713-9e34-eb0a18922af5 (gardenlinux-1877.3-baremetal)<br>**ap-jp-2:** 8edb20a7-f0f2-47f2-9112-faa2569c3893 (gardenlinux-1877.3-baremetal)<br>**ap-sa-1:** dc12514b-b0a8-40dd-b756-a4d27421029c (gardenlinux-1877.3-baremetal)<br>**ap-sa-2:** 617f5ae7-91fd-4149-b783-7a3701a5f420 (gardenlinux-1877.3-baremetal)<br></details> | <details><summary>Download</summary><br>[openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40/openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40.raw)</details> |
| USI | Amazon Web Services | amd64 | `aws-gardener_prod_usi-amd64-1877.3-75df9f40` | <details><summary>21 regions</summary><br>**ap-south-1:** ami-0e904b4c264dbe923<br>**eu-north-1:** ami-016f506d46abb5c06<br>**eu-west-3:** ami-052404d8a97e9ec57<br>**eu-south-1:** ami-002193c185fb2d939<br>**eu-west-2:** ami-0225bc62c7d291107<br>**eu-west-1:** ami-0f737c34ae9ccfe10<br>**ap-northeast-3:** ami-0ecf19a78a7259c02<br>**ap-northeast-2:** ami-029152bf0a15cf306<br>**ap-northeast-1:** ami-0bf003b58ed636124<br>**me-central-1:** ami-0546ca7d7c2e00077<br>**ca-central-1:** ami-0a0081cbd4b479d33<br>**sa-east-1:** ami-086d3b7282338bcd1<br>**ap-southeast-1:** ami-04973efd023e5883f<br>**ap-southeast-2:** ami-00389783d0b7ef01b<br>**us-east-1:** ami-0f5c28bbc45608e9b<br>**us-east-2:** ami-08c7494a2a00b74e5<br>**us-west-1:** ami-0e2290963849dba62<br>**us-west-2:** ami-0fb86d519a38da40f<br>**eu-central-1:** ami-0c6394e4fdbefe8c0<br>**cn-north-1:** ami-0b4c979b27a0a7714<br>**cn-northwest-1:** ami-0cab977e76e274599<br></details> | <details><summary>Download</summary><br>[aws-gardener_prod_usi-amd64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_usi-amd64-1877.3-75df9f40/aws-gardener_prod_usi-amd64-1877.3-75df9f40.raw)</details> |
| USI | Amazon Web Services | arm64 | `aws-gardener_prod_usi-arm64-1877.3-75df9f40` | <details><summary>21 regions</summary><br>**ap-south-1:** ami-029f2b705d69f9d50<br>**eu-north-1:** ami-0b1a9e403ea563206<br>**eu-west-3:** ami-067465814788be84a<br>**eu-south-1:** ami-092d7cf152ef6df29<br>**eu-west-2:** ami-0441298c8ae55a62b<br>**eu-west-1:** ami-012e58abe02f904c1<br>**ap-northeast-3:** ami-08c18c5f1aa7e9fba<br>**ap-northeast-2:** ami-0277ca365657bd9c2<br>**ap-northeast-1:** ami-006a3f35202f6edd4<br>**me-central-1:** ami-0aa9e8af8c777e400<br>**ca-central-1:** ami-0f8225fd2d6009961<br>**sa-east-1:** ami-0e945c537aef91eff<br>**ap-southeast-1:** ami-0f30b29a4428f7cea<br>**ap-southeast-2:** ami-0129e3a207e3e6f9d<br>**us-east-1:** ami-0cc9f69e3a7594e7b<br>**us-east-2:** ami-046243dad95d56f2a<br>**us-west-1:** ami-03ae03953c81a43c1<br>**us-west-2:** ami-0cbe1dbfeda64dc9b<br>**eu-central-1:** ami-0dd2780bfcddbda6b<br>**cn-north-1:** ami-0d993477d25affb3c<br>**cn-northwest-1:** ami-0a7fe5959bb23fab8<br></details> | <details><summary>Download</summary><br>[aws-gardener_prod_usi-arm64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_usi-arm64-1877.3-75df9f40/aws-gardener_prod_usi-arm64-1877.3-75df9f40.raw)</details> |
| USI | Microsoft Azure | amd64 | `azure-gardener_prod_usi-amd64-1877.3-75df9f40` | <details><summary>2 gallery + 0 marketplace images</summary><br>**Gallery Images:**<br>• V2 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2-usi/Versions/1877.3.0<br>• V2 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2-usi/Versions/1877.3.0<br></details> | <details><summary>Download</summary><br>[azure-gardener_prod_usi-amd64-1877.3-75df9f40.vhd](https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_usi-amd64-1877.3-75df9f40/azure-gardener_prod_usi-amd64-1877.3-75df9f40.vhd)</details> |
| USI | Microsoft Azure | arm64 | `azure-gardener_prod_usi-arm64-1877.3-75df9f40` | <details><summary>2 gallery + 0 marketplace images</summary><br>**Gallery Images:**<br>• V2 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2-usi/Versions/1877.3.0<br>• V2 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2-usi/Versions/1877.3.0<br></details> | <details><summary>Download</summary><br>[azure-gardener_prod_usi-arm64-1877.3-75df9f40.vhd](https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_usi-arm64-1877.3-75df9f40/azure-gardener_prod_usi-arm64-1877.3-75df9f40.vhd)</details> |
| USI | Google Cloud Platform | amd64 | `gcp-gardener_prod_usi-amd64-1877.3-75df9f40` | <details><summary>Global availability</summary><br>**Image Name:** gardenlinux-gcp-51db8a4be084c3b640095f4b-1877-3-75df9f40<br>**Project:** sap-se-gcp-gardenlinux<br>**Availability:** Global (all regions)<br></details> | <details><summary>Download</summary><br>[gcp-gardener_prod_usi-amd64-1877.3-75df9f40.gcpimage.tar.gz](https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_usi-amd64-1877.3-75df9f40/gcp-gardener_prod_usi-amd64-1877.3-75df9f40.gcpimage.tar.gz)</details> |
| USI | Google Cloud Platform | arm64 | `gcp-gardener_prod_usi-arm64-1877.3-75df9f40` | <details><summary>Global availability</summary><br>**Image Name:** gardenlinux-gcp-c00f1e20ffeed4d8b80a76b9-1877-3-75df9f40<br>**Project:** sap-se-gcp-gardenlinux<br>**Availability:** Global (all regions)<br></details> | <details><summary>Download</summary><br>[gcp-gardener_prod_usi-arm64-1877.3-75df9f40.gcpimage.tar.gz](https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_usi-arm64-1877.3-75df9f40/gcp-gardener_prod_usi-arm64-1877.3-75df9f40.gcpimage.tar.gz)</details> |
| USI | OpenStack | amd64 | `openstack-gardener_prod_usi-amd64-1877.3-75df9f40` | <details><summary>15 regions</summary><br>**eu-de-1:** 15fc38b3-1cee-4c0a-829a-ef1f7faa1920 (gardenlinux-1877.3)<br>**eu-de-2:** c4e8e8e5-8c92-4c73-b21b-333087e7b092 (gardenlinux-1877.3)<br>**eu-nl-1:** e6f9e054-0613-4204-98c7-84676680418a (gardenlinux-1877.3)<br>**la-br-1:** 04416634-2eaf-44a1-a653-b1ae36bf0e0e (gardenlinux-1877.3)<br>**na-ca-1:** b548d8fd-0e6b-4cb6-9cd1-68b258df00cc (gardenlinux-1877.3)<br>**na-us-1:** 0a97e9af-a1f3-4ae4-bf44-98c432aa436c (gardenlinux-1877.3)<br>**na-us-2:** b1705d73-3f67-427c-8ade-5e245a857338 (gardenlinux-1877.3)<br>**na-us-3:** da3234f1-307c-431e-80bb-9e51dd75673d (gardenlinux-1877.3)<br>**ap-ae-1:** 16f24b39-b9ba-4756-8dcd-82473182f1e4 (gardenlinux-1877.3)<br>**ap-au-1:** 49de0ff1-2c7e-439d-a065-07c837fe48a8 (gardenlinux-1877.3)<br>**ap-cn-1:** 23a94a40-1e9a-4f4b-b2b6-4c167493fbb0 (gardenlinux-1877.3)<br>**ap-jp-1:** 1558417d-14bb-413e-9194-88b2bc5f18aa (gardenlinux-1877.3)<br>**ap-jp-2:** 8d39ad55-2f09-490e-8fa7-0bdf5c854ed7 (gardenlinux-1877.3)<br>**ap-sa-1:** 62be0147-062a-4375-b142-278a811e9754 (gardenlinux-1877.3)<br>**ap-sa-2:** 510d1ff1-4fc6-49ec-ad2f-a0985217dd14 (gardenlinux-1877.3)<br></details> | <details><summary>Download</summary><br>[openstack-gardener_prod_usi-amd64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/openstack-gardener_prod_usi-amd64-1877.3-75df9f40/openstack-gardener_prod_usi-amd64-1877.3-75df9f40.raw)</details> |
| TPM2 | Amazon Web Services | amd64 | `aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40` | <details><summary>19 regions</summary><br>**ap-south-1:** ami-0052561d7bccfe6b7<br>**eu-north-1:** ami-06623180935c63669<br>**eu-west-3:** ami-026632e35fe37f9f4<br>**eu-south-1:** ami-0b60116fac38c2556<br>**eu-west-2:** ami-0ecd844859adf35c5<br>**eu-west-1:** ami-0313333df0acd7eb0<br>**ap-northeast-3:** ami-04e53edbd6ce18fc6<br>**ap-northeast-2:** ami-0ae03e19777874cef<br>**ap-northeast-1:** ami-079e68ce96cc03e78<br>**me-central-1:** ami-01e368d192a479934<br>**ca-central-1:** ami-02cabce931cafcf1f<br>**sa-east-1:** ami-075d5fa3b98620e15<br>**ap-southeast-1:** ami-0a26b478c0a210190<br>**ap-southeast-2:** ami-0f226413240aec4aa<br>**us-east-1:** ami-07dea60f619226e1b<br>**us-east-2:** ami-0e8e852987ee840c3<br>**us-west-1:** ami-0d9314ee5a439ab29<br>**us-west-2:** ami-04dc4614abf1649ab<br>**eu-central-1:** ami-005f7dab618420a91<br></details> | <details><summary>Download</summary><br>[aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40/aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.raw)</details> |
| TPM2 | Amazon Web Services | arm64 | `aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40` | <details><summary>19 regions</summary><br>**ap-south-1:** ami-035b751a08f528e47<br>**eu-north-1:** ami-04c60d1feb092d00f<br>**eu-west-3:** ami-0443172a73fe4fb27<br>**eu-south-1:** ami-02f8a867d02227542<br>**eu-west-2:** ami-06a900dd59c84620d<br>**eu-west-1:** ami-056a9d8447a991bff<br>**ap-northeast-3:** ami-0769caf50f7b7fb6f<br>**ap-northeast-2:** ami-06ad8c60e1093b543<br>**ap-northeast-1:** ami-0b8313d62dfeec78b<br>**me-central-1:** ami-0fa388dcaca7b3baf<br>**ca-central-1:** ami-02e7a07f60a5e0411<br>**sa-east-1:** ami-000ca39b22f2a695c<br>**ap-southeast-1:** ami-04f521cff21b58f50<br>**ap-southeast-2:** ami-02f5afcce42276457<br>**us-east-1:** ami-0a25256d5aaf8fdd7<br>**us-east-2:** ami-07bcfed39a329b612<br>**us-west-1:** ami-0b2e93f36b5a8bff2<br>**us-west-2:** ami-063f4f34958917b5c<br>**eu-central-1:** ami-0b15b442dd5e90d50<br></details> | <details><summary>Download</summary><br>[aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.raw](https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40/aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.raw)</details> |
| TPM2 | Microsoft Azure | amd64 | `azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40` | <details><summary>2 gallery + 0 marketplace images</summary><br>**Gallery Images:**<br>• V2 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2-usi-secureboot/Versions/1877.3.0<br>• V2 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2-usi-secureboot/Versions/1877.3.0<br></details> | <details><summary>Download</summary><br>[azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.vhd](https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40/azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.vhd)</details> |
| TPM2 | Microsoft Azure | arm64 | `azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40` | <details><summary>2 gallery + 0 marketplace images</summary><br>**Gallery Images:**<br>• V2 (public): /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2-usi-secureboot/Versions/1877.3.0<br>• V2 (china): /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2-usi-secureboot/Versions/1877.3.0<br></details> | <details><summary>Download</summary><br>[azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.vhd](https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40/azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.vhd)</details> |
| TPM2 | Google Cloud Platform | amd64 | `gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40` | <details><summary>Global availability</summary><br>**Image Name:** gardenlinux-gcp-b4636aa3660a8d166531aab9-1877-3-75df9f40<br>**Project:** sap-se-gcp-gardenlinux<br>**Availability:** Global (all regions)<br></details> | <details><summary>Download</summary><br>[gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.gcpimage.tar.gz](https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40/gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.gcpimage.tar.gz)</details> |
| TPM2 | Google Cloud Platform | arm64 | `gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40` | <details><summary>Global availability</summary><br>**Image Name:** gardenlinux-gcp-63fd9d7dd465420fd4e499ab-1877-3-75df9f40<br>**Project:** sap-se-gcp-gardenlinux<br>**Availability:** Global (all regions)<br></details> | <details><summary>Download</summary><br>[gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.gcpimage.tar.gz](https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40/gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.gcpimage.tar.gz)</details> |

</details>

<details>
<summary>📝 Detailed View</summary>

<details>
<summary>Variant - Default</summary>

### Variant - Default

<details>
<summary>ALI - Alibaba Cloud</summary>

#### ALI - Alibaba Cloud

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: ali-gardener_prod-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/ali-gardener_prod-amd64-1877.3-75df9f40/ali-gardener_prod-amd64-1877.3-75df9f40.qcow2
  regions:
    - region: cn-qingdao
      image_id: m-m5efm8l2bltkbloui235
    - region: cn-beijing
      image_id: m-2zee5ebi20ltzy5et7in
    - region: cn-zhangjiakou
      image_id: m-8vbddy2wfex9nb29afcy
    - region: cn-huhehaote
      image_id: m-hp3bx14og6cw9thujw1d
    - region: cn-wulanchabu
      image_id: m-0jlh1iq2f3bryb5okjdk
    - region: cn-hangzhou
      image_id: m-bp13aseh5a2wn0s5rdz6
    - region: cn-shanghai
      image_id: m-uf61jbe9n8a9291h4u21
    - region: cn-nanjing
      image_id: m-gc77bfbctuzphl2bpk0o
    - region: cn-shenzhen
      image_id: m-wz9gio8m5ey0foj0g4xx
    - region: cn-heyuan
      image_id: m-f8zdn54v0blnsafxb1t5
    - region: cn-guangzhou
      image_id: m-7xv0q5feffsxxyttxdy9
    - region: cn-fuzhou
      image_id: m-gw07bfbctuzphl2bpk0p
    - region: cn-wuhan-lr
      image_id: m-n4a1u2avlb9pq0u5bdms
    - region: cn-chengdu
      image_id: m-2vc5saul2saa2z57h216
    - region: cn-hongkong
      image_id: m-j6c4zk6mwb2673iq5wrz
    - region: ap-northeast-1
      image_id: m-6weibwo3vrt7ar7nelc9
    - region: ap-northeast-2
      image_id: m-mj73oldn06th2vy0ymhv
    - region: ap-southeast-1
      image_id: m-t4ngrf81d0fohwq493pw
    - region: ap-southeast-3
      image_id: m-8psd64gzc1eru0qld7cc
    - region: ap-southeast-6
      image_id: m-5tsdd6k3z1vvdyyio7zn
    - region: ap-southeast-5
      image_id: m-k1aj4usnhqcssa2fpy0c
    - region: ap-southeast-7
      image_id: m-0jo6uwekvn0gnwhwnq3s
    - region: us-east-1
      image_id: m-0xi8netpfc2fdwfstz3c
    - region: us-west-1
      image_id: m-rj9gwpx907qv6p6x8w45
    - region: na-south-1
      image_id: m-4hfi34x77oaeznwuulq6
    - region: eu-west-1
      image_id: m-d7o2ny5xc0m3kacxjbem
    - region: me-east-1
      image_id: m-eb39mgohcec6gaynet9l
    - region: eu-central-1
      image_id: m-gw86dlqmpaugljiykx91
```

</details>

</details>

<details>
<summary>AWS - Amazon Web Services</summary>

#### AWS - Amazon Web Services

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: aws-gardener_prod-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod-amd64-1877.3-75df9f40/aws-gardener_prod-amd64-1877.3-75df9f40.raw
  regions:
    - region: ap-south-1
      image_id: ami-00c6adf1de4dd746a
    - region: eu-north-1
      image_id: ami-07ad3940828172b90
    - region: eu-west-3
      image_id: ami-071f4f48679d86638
    - region: eu-south-1
      image_id: ami-0b10af1a19df9f038
    - region: eu-west-2
      image_id: ami-0e2b7fe07573b71cd
    - region: eu-west-1
      image_id: ami-01c547eb85d61da61
    - region: ap-northeast-3
      image_id: ami-0dad917ede94cd3c7
    - region: ap-northeast-2
      image_id: ami-0ecbeaf40d4643016
    - region: ap-northeast-1
      image_id: ami-0b7225242babad11c
    - region: me-central-1
      image_id: ami-0d298e552bf051bc7
    - region: ca-central-1
      image_id: ami-0af8422162c8f056e
    - region: sa-east-1
      image_id: ami-05d885175e942fc80
    - region: ap-southeast-1
      image_id: ami-0a9802680adf7e430
    - region: ap-southeast-2
      image_id: ami-07ed6f1e62fbd6d66
    - region: us-east-1
      image_id: ami-055a0ce37433fcdee
    - region: us-east-2
      image_id: ami-07e9069631850755a
    - region: us-west-1
      image_id: ami-08c18abab76066f71
    - region: us-west-2
      image_id: ami-00eca0475f90a1f8c
    - region: eu-central-1
      image_id: ami-0198822fa7d539f8c
    - region: cn-north-1
      image_id: ami-093c993faaca89b4d
    - region: cn-northwest-1
      image_id: ami-05e1cc73d997d67b7
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: aws-gardener_prod-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod-arm64-1877.3-75df9f40/aws-gardener_prod-arm64-1877.3-75df9f40.raw
  regions:
    - region: ap-south-1
      image_id: ami-00cd00c30d19609a2
    - region: eu-north-1
      image_id: ami-0a969a1a1c4726831
    - region: eu-west-3
      image_id: ami-0b579f6c70b7c4fe6
    - region: eu-south-1
      image_id: ami-06c38608e2e7223d3
    - region: eu-west-2
      image_id: ami-005c7058c3923b2eb
    - region: eu-west-1
      image_id: ami-0395c3cd38a0a5cd6
    - region: ap-northeast-3
      image_id: ami-0db3697cea87a5104
    - region: ap-northeast-2
      image_id: ami-084444f62c7c580fb
    - region: ap-northeast-1
      image_id: ami-017237dd9abeae8dd
    - region: me-central-1
      image_id: ami-08efdb3153d0cd184
    - region: ca-central-1
      image_id: ami-05b535ae9418fee3d
    - region: sa-east-1
      image_id: ami-036ded98bad763e3c
    - region: ap-southeast-1
      image_id: ami-03fcefb2fd18519d0
    - region: ap-southeast-2
      image_id: ami-040f9d0caa5d79e84
    - region: us-east-1
      image_id: ami-04110d6a1970e748c
    - region: us-east-2
      image_id: ami-0c8dc664a21d5ca08
    - region: us-west-1
      image_id: ami-0ddc462d075935666
    - region: us-west-2
      image_id: ami-0e67c2546e54fed06
    - region: eu-central-1
      image_id: ami-06a2a1e7da947b192
    - region: cn-north-1
      image_id: ami-0b3755339496a3158
    - region: cn-northwest-1
      image_id: ami-06fc0f74b500d2d82
```

</details>

</details>

<details>
<summary>AZURE - Microsoft Azure</summary>

#### AZURE - Microsoft Azure

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: azure-gardener_prod-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod-amd64-1877.3-75df9f40/azure-gardener_prod-amd64-1877.3-75df9f40.vhd
  gallery_images:
    - hyper_v_generation: V1
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2/Versions/1877.3.0
    - hyper_v_generation: V1
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2/Versions/1877.3.0
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: azure-gardener_prod-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod-arm64-1877.3-75df9f40/azure-gardener_prod-arm64-1877.3-75df9f40.vhd
  gallery_images:
    - hyper_v_generation: V2
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2/Versions/1877.3.0
```

</details>

</details>

<details>
<summary>GCP - Google Cloud Platform</summary>

#### GCP - Google Cloud Platform

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: gcp-gardener_prod-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod-amd64-1877.3-75df9f40/gcp-gardener_prod-amd64-1877.3-75df9f40.gcpimage.tar.gz
  image_name: gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1877-3-75df9f40
  project: sap-se-gcp-gardenlinux
  availability: Global (all regions)
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: gcp-gardener_prod-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod-arm64-1877.3-75df9f40/gcp-gardener_prod-arm64-1877.3-75df9f40.gcpimage.tar.gz
  image_name: gardenlinux-gcp-c8504d3c3e67cf2fc7c3408c-1877-3-75df9f40
  project: sap-se-gcp-gardenlinux
  availability: Global (all regions)
```

</details>

</details>

<details>
<summary>OPENSTACK - OpenStack</summary>

#### OPENSTACK - OpenStack

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: openstack-gardener_prod-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/openstack-gardener_prod-amd64-1877.3-75df9f40/openstack-gardener_prod-amd64-1877.3-75df9f40.raw
  regions:
    - region: eu-de-1
      image_id: ed3b4c3d-941f-456a-a551-bd52b8397443
      image_name: gardenlinux-1877.3
    - region: eu-de-2
      image_id: 5ea6fb4f-20fc-43b8-8ffe-af8da6d61d6a
      image_name: gardenlinux-1877.3
    - region: eu-nl-1
      image_id: ac9b5d43-ff53-494d-8adf-2249c324a9db
      image_name: gardenlinux-1877.3
    - region: la-br-1
      image_id: 404f22a3-9822-4696-a60f-8566eedb93e3
      image_name: gardenlinux-1877.3
    - region: na-ca-1
      image_id: b69b72f3-574a-4f76-b4eb-ac9185ea2681
      image_name: gardenlinux-1877.3
    - region: na-us-1
      image_id: 40e99366-f13b-402a-a264-e7e4773ab8ba
      image_name: gardenlinux-1877.3
    - region: na-us-2
      image_id: c50200c6-95fd-4a97-bef2-90b2d6afa3d3
      image_name: gardenlinux-1877.3
    - region: na-us-3
      image_id: d5b1d8c0-3420-4a82-931d-0506a6b8f166
      image_name: gardenlinux-1877.3
    - region: ap-ae-1
      image_id: 81c26cb7-c515-4610-949a-92c275640325
      image_name: gardenlinux-1877.3
    - region: ap-au-1
      image_id: 2d6e3edd-5596-41e6-a640-4b1b8e7310e7
      image_name: gardenlinux-1877.3
    - region: ap-cn-1
      image_id: 3564b5ef-9b37-4926-bb23-5655cf90de69
      image_name: gardenlinux-1877.3
    - region: ap-jp-1
      image_id: 2ff61187-f004-4317-bd4c-a17d93b475bc
      image_name: gardenlinux-1877.3
    - region: ap-jp-2
      image_id: 2bc58951-9bf7-445b-a6e4-f634c7522d9b
      image_name: gardenlinux-1877.3
    - region: ap-sa-1
      image_id: e4a4aa92-335a-454b-83bb-643cb918cf6a
      image_name: gardenlinux-1877.3
    - region: ap-sa-2
      image_id: d3ac5df8-ce38-4a23-b611-dfef6b7a0db9
      image_name: gardenlinux-1877.3
```

</details>

</details>

<details>
<summary>OPENSTACKBAREMETAL - OpenStack Baremetal</summary>

#### OPENSTACKBAREMETAL - OpenStack Baremetal

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40/openstackbaremetal-gardener_prod-amd64-1877.3-75df9f40.raw
  regions:
    - region: eu-de-1
      image_id: 01c3ab26-5b93-4655-a743-1fef60f64b53
      image_name: gardenlinux-1877.3-baremetal
    - region: eu-de-2
      image_id: 7488d07b-65f1-4b85-8df8-13244b895d71
      image_name: gardenlinux-1877.3-baremetal
    - region: eu-nl-1
      image_id: 1926a818-55d5-49e1-9af8-eab8450705eb
      image_name: gardenlinux-1877.3-baremetal
    - region: la-br-1
      image_id: 6fda686d-d2f7-4018-ab4c-1250e898197a
      image_name: gardenlinux-1877.3-baremetal
    - region: na-ca-1
      image_id: a032ecc1-3bee-4d65-9f68-3e3f99e2c291
      image_name: gardenlinux-1877.3-baremetal
    - region: na-us-1
      image_id: d663d5f1-1b44-41af-9039-e36cc64a5920
      image_name: gardenlinux-1877.3-baremetal
    - region: na-us-2
      image_id: 818bbfdd-4ee4-49ee-8294-dc3a3c66971f
      image_name: gardenlinux-1877.3-baremetal
    - region: na-us-3
      image_id: b154b48b-050f-48d6-997f-b6c2756079a6
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-ae-1
      image_id: 5992e19c-2ca2-47be-ae55-50e2fd26b662
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-au-1
      image_id: 986403a6-e254-4689-8f81-e32dc33c9b64
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-cn-1
      image_id: 0c794890-a690-4881-b0c2-39a939b020e2
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-jp-1
      image_id: f5be2c30-8e8e-4713-9e34-eb0a18922af5
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-jp-2
      image_id: 8edb20a7-f0f2-47f2-9112-faa2569c3893
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-sa-1
      image_id: dc12514b-b0a8-40dd-b756-a4d27421029c
      image_name: gardenlinux-1877.3-baremetal
    - region: ap-sa-2
      image_id: 617f5ae7-91fd-4149-b783-7a3701a5f420
      image_name: gardenlinux-1877.3-baremetal
```

</details>

</details>

</details>

<details>
<summary>Variant - USI (Unified System Image)</summary>

### Variant - USI (Unified System Image)

<details>
<summary>AWS - Amazon Web Services</summary>

#### AWS - Amazon Web Services

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: aws-gardener_prod_usi-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_usi-amd64-1877.3-75df9f40/aws-gardener_prod_usi-amd64-1877.3-75df9f40.raw
  regions:
    - region: ap-south-1
      image_id: ami-0e904b4c264dbe923
    - region: eu-north-1
      image_id: ami-016f506d46abb5c06
    - region: eu-west-3
      image_id: ami-052404d8a97e9ec57
    - region: eu-south-1
      image_id: ami-002193c185fb2d939
    - region: eu-west-2
      image_id: ami-0225bc62c7d291107
    - region: eu-west-1
      image_id: ami-0f737c34ae9ccfe10
    - region: ap-northeast-3
      image_id: ami-0ecf19a78a7259c02
    - region: ap-northeast-2
      image_id: ami-029152bf0a15cf306
    - region: ap-northeast-1
      image_id: ami-0bf003b58ed636124
    - region: me-central-1
      image_id: ami-0546ca7d7c2e00077
    - region: ca-central-1
      image_id: ami-0a0081cbd4b479d33
    - region: sa-east-1
      image_id: ami-086d3b7282338bcd1
    - region: ap-southeast-1
      image_id: ami-04973efd023e5883f
    - region: ap-southeast-2
      image_id: ami-00389783d0b7ef01b
    - region: us-east-1
      image_id: ami-0f5c28bbc45608e9b
    - region: us-east-2
      image_id: ami-08c7494a2a00b74e5
    - region: us-west-1
      image_id: ami-0e2290963849dba62
    - region: us-west-2
      image_id: ami-0fb86d519a38da40f
    - region: eu-central-1
      image_id: ami-0c6394e4fdbefe8c0
    - region: cn-north-1
      image_id: ami-0b4c979b27a0a7714
    - region: cn-northwest-1
      image_id: ami-0cab977e76e274599
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: aws-gardener_prod_usi-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_usi-arm64-1877.3-75df9f40/aws-gardener_prod_usi-arm64-1877.3-75df9f40.raw
  regions:
    - region: ap-south-1
      image_id: ami-029f2b705d69f9d50
    - region: eu-north-1
      image_id: ami-0b1a9e403ea563206
    - region: eu-west-3
      image_id: ami-067465814788be84a
    - region: eu-south-1
      image_id: ami-092d7cf152ef6df29
    - region: eu-west-2
      image_id: ami-0441298c8ae55a62b
    - region: eu-west-1
      image_id: ami-012e58abe02f904c1
    - region: ap-northeast-3
      image_id: ami-08c18c5f1aa7e9fba
    - region: ap-northeast-2
      image_id: ami-0277ca365657bd9c2
    - region: ap-northeast-1
      image_id: ami-006a3f35202f6edd4
    - region: me-central-1
      image_id: ami-0aa9e8af8c777e400
    - region: ca-central-1
      image_id: ami-0f8225fd2d6009961
    - region: sa-east-1
      image_id: ami-0e945c537aef91eff
    - region: ap-southeast-1
      image_id: ami-0f30b29a4428f7cea
    - region: ap-southeast-2
      image_id: ami-0129e3a207e3e6f9d
    - region: us-east-1
      image_id: ami-0cc9f69e3a7594e7b
    - region: us-east-2
      image_id: ami-046243dad95d56f2a
    - region: us-west-1
      image_id: ami-03ae03953c81a43c1
    - region: us-west-2
      image_id: ami-0cbe1dbfeda64dc9b
    - region: eu-central-1
      image_id: ami-0dd2780bfcddbda6b
    - region: cn-north-1
      image_id: ami-0d993477d25affb3c
    - region: cn-northwest-1
      image_id: ami-0a7fe5959bb23fab8
```

</details>

</details>

<details>
<summary>AZURE - Microsoft Azure</summary>

#### AZURE - Microsoft Azure

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: azure-gardener_prod_usi-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_usi-amd64-1877.3-75df9f40/azure-gardener_prod_usi-amd64-1877.3-75df9f40.vhd
  gallery_images:
    - hyper_v_generation: V2
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2-usi/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2-usi/Versions/1877.3.0
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: azure-gardener_prod_usi-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_usi-arm64-1877.3-75df9f40/azure-gardener_prod_usi-arm64-1877.3-75df9f40.vhd
  gallery_images:
    - hyper_v_generation: V2
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2-usi/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2-usi/Versions/1877.3.0
```

</details>

</details>

<details>
<summary>GCP - Google Cloud Platform</summary>

#### GCP - Google Cloud Platform

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: gcp-gardener_prod_usi-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_usi-amd64-1877.3-75df9f40/gcp-gardener_prod_usi-amd64-1877.3-75df9f40.gcpimage.tar.gz
  image_name: gardenlinux-gcp-51db8a4be084c3b640095f4b-1877-3-75df9f40
  project: sap-se-gcp-gardenlinux
  availability: Global (all regions)
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: gcp-gardener_prod_usi-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_usi-arm64-1877.3-75df9f40/gcp-gardener_prod_usi-arm64-1877.3-75df9f40.gcpimage.tar.gz
  image_name: gardenlinux-gcp-c00f1e20ffeed4d8b80a76b9-1877-3-75df9f40
  project: sap-se-gcp-gardenlinux
  availability: Global (all regions)
```

</details>

</details>

<details>
<summary>OPENSTACK - OpenStack</summary>

#### OPENSTACK - OpenStack

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: openstack-gardener_prod_usi-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/openstack-gardener_prod_usi-amd64-1877.3-75df9f40/openstack-gardener_prod_usi-amd64-1877.3-75df9f40.raw
  regions:
    - region: eu-de-1
      image_id: 15fc38b3-1cee-4c0a-829a-ef1f7faa1920
      image_name: gardenlinux-1877.3
    - region: eu-de-2
      image_id: c4e8e8e5-8c92-4c73-b21b-333087e7b092
      image_name: gardenlinux-1877.3
    - region: eu-nl-1
      image_id: e6f9e054-0613-4204-98c7-84676680418a
      image_name: gardenlinux-1877.3
    - region: la-br-1
      image_id: 04416634-2eaf-44a1-a653-b1ae36bf0e0e
      image_name: gardenlinux-1877.3
    - region: na-ca-1
      image_id: b548d8fd-0e6b-4cb6-9cd1-68b258df00cc
      image_name: gardenlinux-1877.3
    - region: na-us-1
      image_id: 0a97e9af-a1f3-4ae4-bf44-98c432aa436c
      image_name: gardenlinux-1877.3
    - region: na-us-2
      image_id: b1705d73-3f67-427c-8ade-5e245a857338
      image_name: gardenlinux-1877.3
    - region: na-us-3
      image_id: da3234f1-307c-431e-80bb-9e51dd75673d
      image_name: gardenlinux-1877.3
    - region: ap-ae-1
      image_id: 16f24b39-b9ba-4756-8dcd-82473182f1e4
      image_name: gardenlinux-1877.3
    - region: ap-au-1
      image_id: 49de0ff1-2c7e-439d-a065-07c837fe48a8
      image_name: gardenlinux-1877.3
    - region: ap-cn-1
      image_id: 23a94a40-1e9a-4f4b-b2b6-4c167493fbb0
      image_name: gardenlinux-1877.3
    - region: ap-jp-1
      image_id: 1558417d-14bb-413e-9194-88b2bc5f18aa
      image_name: gardenlinux-1877.3
    - region: ap-jp-2
      image_id: 8d39ad55-2f09-490e-8fa7-0bdf5c854ed7
      image_name: gardenlinux-1877.3
    - region: ap-sa-1
      image_id: 62be0147-062a-4375-b142-278a811e9754
      image_name: gardenlinux-1877.3
    - region: ap-sa-2
      image_id: 510d1ff1-4fc6-49ec-ad2f-a0985217dd14
      image_name: gardenlinux-1877.3
```

</details>

</details>

</details>

<details>
<summary>Variant - TPM2 Trusted Boot</summary>

### Variant - TPM2 Trusted Boot

<details>
<summary>AWS - Amazon Web Services</summary>

#### AWS - Amazon Web Services

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40/aws-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.raw
  regions:
    - region: ap-south-1
      image_id: ami-0052561d7bccfe6b7
    - region: eu-north-1
      image_id: ami-06623180935c63669
    - region: eu-west-3
      image_id: ami-026632e35fe37f9f4
    - region: eu-south-1
      image_id: ami-0b60116fac38c2556
    - region: eu-west-2
      image_id: ami-0ecd844859adf35c5
    - region: eu-west-1
      image_id: ami-0313333df0acd7eb0
    - region: ap-northeast-3
      image_id: ami-04e53edbd6ce18fc6
    - region: ap-northeast-2
      image_id: ami-0ae03e19777874cef
    - region: ap-northeast-1
      image_id: ami-079e68ce96cc03e78
    - region: me-central-1
      image_id: ami-01e368d192a479934
    - region: ca-central-1
      image_id: ami-02cabce931cafcf1f
    - region: sa-east-1
      image_id: ami-075d5fa3b98620e15
    - region: ap-southeast-1
      image_id: ami-0a26b478c0a210190
    - region: ap-southeast-2
      image_id: ami-0f226413240aec4aa
    - region: us-east-1
      image_id: ami-07dea60f619226e1b
    - region: us-east-2
      image_id: ami-0e8e852987ee840c3
    - region: us-west-1
      image_id: ami-0d9314ee5a439ab29
    - region: us-west-2
      image_id: ami-04dc4614abf1649ab
    - region: eu-central-1
      image_id: ami-005f7dab618420a91
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40/aws-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.raw
  regions:
    - region: ap-south-1
      image_id: ami-035b751a08f528e47
    - region: eu-north-1
      image_id: ami-04c60d1feb092d00f
    - region: eu-west-3
      image_id: ami-0443172a73fe4fb27
    - region: eu-south-1
      image_id: ami-02f8a867d02227542
    - region: eu-west-2
      image_id: ami-06a900dd59c84620d
    - region: eu-west-1
      image_id: ami-056a9d8447a991bff
    - region: ap-northeast-3
      image_id: ami-0769caf50f7b7fb6f
    - region: ap-northeast-2
      image_id: ami-06ad8c60e1093b543
    - region: ap-northeast-1
      image_id: ami-0b8313d62dfeec78b
    - region: me-central-1
      image_id: ami-0fa388dcaca7b3baf
    - region: ca-central-1
      image_id: ami-02e7a07f60a5e0411
    - region: sa-east-1
      image_id: ami-000ca39b22f2a695c
    - region: ap-southeast-1
      image_id: ami-04f521cff21b58f50
    - region: ap-southeast-2
      image_id: ami-02f5afcce42276457
    - region: us-east-1
      image_id: ami-0a25256d5aaf8fdd7
    - region: us-east-2
      image_id: ami-07bcfed39a329b612
    - region: us-west-1
      image_id: ami-0b2e93f36b5a8bff2
    - region: us-west-2
      image_id: ami-063f4f34958917b5c
    - region: eu-central-1
      image_id: ami-0b15b442dd5e90d50
```

</details>

</details>

<details>
<summary>AZURE - Microsoft Azure</summary>

#### AZURE - Microsoft Azure

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40/azure-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.vhd
  gallery_images:
    - hyper_v_generation: V2
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2-usi-secureboot/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2-usi-secureboot/Versions/1877.3.0
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40/azure-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.vhd
  gallery_images:
    - hyper_v_generation: V2
      azure_cloud: public
      image_id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2-usi-secureboot/Versions/1877.3.0
    - hyper_v_generation: V2
      azure_cloud: china
      image_id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2-usi-secureboot/Versions/1877.3.0
```

</details>

</details>

<details>
<summary>GCP - Google Cloud Platform</summary>

#### GCP - Google Cloud Platform

<details>
<summary>amd64</summary>

##### amd64

```
- flavor: gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40/gcp-gardener_prod_tpm2_trustedboot-amd64-1877.3-75df9f40.gcpimage.tar.gz
  image_name: gardenlinux-gcp-b4636aa3660a8d166531aab9-1877-3-75df9f40
  project: sap-se-gcp-gardenlinux
  availability: Global (all regions)
```

</details>

<details>
<summary>arm64</summary>

##### arm64

```
- flavor: gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40
  download_url: https://gardenlinux-github-releases.s3.amazonaws.com/objects/gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40/gcp-gardener_prod_tpm2_trustedboot-arm64-1877.3-75df9f40.gcpimage.tar.gz
  image_name: gardenlinux-gcp-63fd9d7dd465420fd4e499ab-1877-3-75df9f40
  project: sap-se-gcp-gardenlinux
  availability: Global (all regions)
```

</details>

</details>

</details>


</details>


## Kernel Module Build Container (kmodbuild)
```
ghcr.io/gardenlinux/gardenlinux/kmodbuild:1877.3
```

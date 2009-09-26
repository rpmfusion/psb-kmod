# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%define buildforkernels current

Name:		psb-kmod
Version:	4.41.1
Release:	10%{?dist}
Summary:	Kernel module for Poulsbo graphics chipsets

Group:		System Environment/Kernel
License:	GPLv2+
URL:		http://ppa.launchpad.net/ubuntu-mobile/ubuntu/pool/main/p/psb-kernel-source/
Source0:	http://ppa.launchpad.net/ubuntu-mobile/ubuntu/pool/main/p/psb-kernel-source/psb-kernel-source_%{version}.orig.tar.gz

# upstream status for all patches: upstream? heh. good joke.

# kernel 2.6.29 build patch, from mandriva
Patch0:		psb-kmd-4.34-current_euid.patch
# kernel 2.6.30 build patch, by me
Patch1:		psb-kmod-4.41.1_irqreturn.patch
# kernel 2.6.30 build patch, by me (mandriva has the same patch
# independently arrived at, they call it dev_set_name.patch)
Patch2:		psb-kmod-4.41.1_busid.patch
# kernel 2.6.30 build patch, from ubuntu via mandriva
Patch3:		psb-kernel-source-4.41.1-agp_memory.patch
# rename drm.ko to drm-psb.ko so we don't get dependency ickiness due
# to competition with the 'real' drm.ko (from mandriva)
Patch4:		psb-kernel-source-4.41.1-drmpsb.patch
# define intel framebuffer driver (fixes a build problem)
# (from mandriva)
Patch5:		psb-kernel-source-4.41.1-i2c-intelfb.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch:	i586 i686

# get the needed BuildRequires (in parts depending on what we build for)
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
%{summary}.


%prep
%{?kmodtool_check}
kmodtool  --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null


%setup -q -c

for kernel_version  in %{?kernel_versions} ; do
    cp -a psb-kernel-source-%{version} _kmod_build_${kernel_version%%___*}
 pushd _kmod_build_${kernel_version%%___*}
  if [[ $kernel_version > "2.6.28.99" ]]; then
%patch0 -p1 -b .build
%patch5 -p1 -b .intelfb
  fi
  if [[ $kernel_version > "2.6.29.99" ]]; then
%patch1 -p1 -b .irqreturn
%patch2 -p1 -b .busid
  fi
  if [[ $kernel_version > "2.6.30.99" ]]; then
%patch3 -p1 -b .agp
  fi
%patch4 -p1 -b .drmpsb
 popd
done


%build
for kv in %{?kernel_versions} ; do
    d=$PWD/_kmod_build_${kv%%___*}
    pushd $d
    make LINUXDIR="${kv##*___}" DRM_MODULES=psb
    popd
done


%install
rm -rf $RPM_BUILD_ROOT
for kv in %{?kernel_versions} ; do
    d=$RPM_BUILD_ROOT%{kmodinstdir_prefix}/${kv%%___*}/%{kmodinstdir_postfix}
    install -dm 755 $d
    install -pm 755 _kmod_build_${kv%%___*}/psb.ko $d
    install -pm 755 _kmod_build_${kv%%___*}/drm-psb.ko $d
done

%{?akmod_install}


%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Thu Sep 24 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-10
- add several patches from mandriva:
	+ replace build.patch with mdv's current_euid.patch (cleaner)
	+ replace agpmem.patch with mdv's agp_memory.patch (cleaner)
	+ add drmpsb.patch (builds drm module as drm-psb.ko)
	+ add intelfb.patch (cleaner fix for a build issue which
	  used to be fixed in my old build.patch)

* Fri Aug 28 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-9
- initial cut at a 2.6.31 patch (taken from corresponding changes in
  upstream files)

* Mon Aug 24 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-8
- try just 'i586 i686' for exclusivearch

* Mon Aug 24 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-7
- drop exclusivearch for now, it is being annoying
- improve irqreturn.patch, should prevent spurious interrupt problem
  (thanks to Konstantin Kletschke)

* Thu Aug 20 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-6
- exclusivearch ix86 (there's no 64-bit poulsbo hardware)
- and drop libdrm-poulsbo BR (doesn't seem necessary)

* Wed Aug 19 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-5
- bump revision to make sure correct patches included

* Mon Aug 17 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-4
- try and fix for 2.6.30

* Tue Aug 11 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-3
- rebuild with changed libdrm-poulsbo just to make sure it works

* Mon Aug 10 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-2
- use AkmodsBuildRequires (so the akmod requires work right)

* Mon Aug 10 2009 Adam Williamson <adamwill AT shaw.ca> - 4.41.1-1
- New version

* Wed May 13 2009 Adam Williamson <adamwill AT shaw.ca> - 4.40-1
- Initial package


# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%define buildforkernels newest

Name:		psb-kmod
Version:	4.41.1
Release:	15%{?dist}.5
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
# Fix build for 2.6.32 (from Gentoo via Mandriva)
Patch6:		psb-kernel-source-4.41.1-2.6.32.patch
# Fix build for 2.6.34 (Eric Piel: https://patchwork.kernel.org/patch/90678/ )
Patch7:		psb-kmod-4.41.1-2.6.34.patch
# From Matthew Garrett: declare module firmware
Patch8:		0001-psb-Declare-firmware.patch
# From Matthew Garrett: clean up debug error
Patch9:		0002-psb-If-not-asking-for-debug-is-an-error-I-want-to-be.patch
# From Matthew Garrett: fix framebuffer
Patch10:	0003-psb-Fix-framebuffer.patch
# From Lubomir Rintel: fix build for 2.6.35
Patch11:	psb-kmod-4.41.1-overflow.patch
Patch12:	0001-Attempt-to-deal-with-psb_dispatch_raster-NULL-derefe.patch
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
  if [[ $kernel_version > "2.6.31.99" ]]; then
%patch6 -p1 -b .build2632
  fi
%patch4 -p1 -b .drmpsb
%patch7 -p0 -b .build2634
%patch8 -p1 -b .firmware
%patch9 -p1 -b .debug
%patch10 -p1 -b .framebuffer
%patch11 -p1 -b .overflow
%patch12 -p1 -b .nullderef
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
* Wed Nov 02 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.41.1-15.5
- rebuild for updated kernel

* Sat Oct 22 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.41.1-15.4
- rebuild for updated kernel

* Sun Sep 18 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.41.1-15.3
- rebuild for updated kernel

* Sat Sep 03 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.41.1-15.2
- rebuild for updated kernel

* Fri Aug 19 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.41.1-15.1
- rebuild for updated kernel

* Sun Jul 10 2011 Nicolas Chauvet <kwizart@gmail.com> - 4.41.1-15
- Add patch from Lubomir Rintel - rfbz#1676

* Sat May 28 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.12
- rebuild for updated kernel

* Thu May 05 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.11
- rebuild for updated kernel

* Sun Apr 24 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.10
- rebuild for updated kernel

* Mon Apr 04 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.9
- rebuild for updated kernel

* Sat Feb 12 2011 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.8
- rebuild for updated kernel

* Fri Dec 24 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.7
- rebuild for updated kernel

* Wed Dec 22 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.6
- rebuild for updated kernel

* Mon Dec 20 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.5
- rebuild for updated kernel

* Fri Dec 17 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.4
- rebuild for updated kernel

* Mon Dec 06 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.3
- rebuilt

* Mon Nov 01 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.2
- rebuild for F-14 kernel

* Fri Oct 29 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-14.1
- rebuild for F-14 kernel

* Fri Sep 17 2010 Adam Williamson <adamwill AT shaw DOT ca> - 4.41.1-14
- add a patch from Lubomir Rintel to fix for kernel 2.6.35

* Sat Sep 11 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-13.6
- rebuild for new kernel

* Fri Sep 10 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-13.5
- rebuild for new kernel

* Sat Aug 28 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-13.4
- rebuild for new kernel

* Fri Aug 20 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-13.3
- rebuild for new kernel

* Wed Aug 11 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-13.2
- rebuild for new kernel

* Sun Aug 08 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-13.1
- rebuild for new kernel

* Wed Aug 04 2010 Adam Williamson <adamwill AT shaw DOT ca> - 4.41.1-13
- add three patches from Matthew Garrett:
	+ Declare-firmware.patch (declare module firmware)
	+ If-not-asking-for-debug...patch (clean up debug error)
	+ Fix-framebuffer.patch (fix framebuffer)

* Tue Jul 27 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-12.1
- rebuild for new kernel

* Thu Jul 22 2010 Adam Williamson <adamwill AT shaw DOT ca> - 4.41.1-12
- add 2.6.34.patch (from Eric Piel, fixes build on 2.6.34)

* Fri May 21 2010 Adam Williamson <adamwill AT shaw DOT ca> - 4.41.1-11
- add 2.6.32.patch (from Gentoo via Mandriva, fixes build on 2.6.32)

* Thu Feb 11 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.10
- rebuild for new kernel

* Mon Feb 08 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.9
- rebuild for new kernel

* Thu Feb 04 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.8
- rebuild for new kernel

* Fri Jan 22 2010 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.7
- rebuild for new kernel

* Sat Dec 26 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.6
- rebuild for new kernel

* Sun Dec 06 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.5
- rebuild for new kernel

* Sun Nov 22 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.4
- rebuild for new kernels

* Thu Nov 05 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.3
- rebuild for new kernels

* Tue Oct 20 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.2
- rebuild for new kernels

* Wed Sep 30 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 4.41.1-10.1
- rebuild for new kernels

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


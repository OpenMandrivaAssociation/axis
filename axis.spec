%define name       axis
%define version    1.2.1
%define archivever 1_2_1
%define release    %mkrel 2.2.2
%define section    free
%define gcj_support 1

Name:          %{name}
Version:       %{version}
Release:       %{release}
Epoch:         0
Summary:       A SOAP implementation in Java
License:       Apache License
Group:         Development/Java
Url:           http://ws.apache.org/%{name}/
Source0:       %{name}-src-%{archivever}-RHCLEAN.tar.bz2
Patch1:        %{name}-bz152255.patch
Patch2:        %{name}-imageio.patch
Patch3:        %{name}-objectweb.patch
Patch4:        %{name}-%{version}-DH.patch
BuildRequires: jpackage-utils >= 0:1.5
BuildRequires: java-devel
BuildRequires: ant >= 0:1.6
BuildRequires: ant-nodeps
# Mandatory requires
BuildRequires: jaf
BuildRequires: jakarta-commons-discovery
BuildRequires: jakarta-commons-httpclient
BuildRequires: jakarta-commons-logging
BuildRequires: javamail
BuildRequires: jaxp_parser_impl
BuildRequires: log4j
BuildRequires: servletapi5
BuildRequires: wsdl4j
# optional requires
BuildRequires: jsse
BuildRequires: junit
BuildRequires: oro
#BuildRequires: jms
BuildRequires: castor
#BuildRequires: xml-security

Requires:      java
Requires:      jpackage-utils >= 0:1.5
Requires:      jaf
Requires:      jakarta-commons-discovery
Requires:      jakarta-commons-logging
Requires:      jakarta-commons-httpclient
Requires:      javamail
Requires:      jaxp_parser_impl
Requires:      log4j
Requires:      wsdl4j

%if %{gcj_support}
Requires(post): java-gcj-compat
Requires(postun): java-gcj-compat
BuildRequires:  java-gcj-compat-devel
%else
Buildarch:      noarch
%endif
BuildRoot:     %{_tmppath}/%{name}-%{version}-buildroot

%description
Apache AXIS is an implementation of the SOAP ("Simple Object Access Protocol")
submission to W3C.

From the draft W3C specification:

SOAP is a lightweight protocol for exchange of information in a decentralized,
distributed environment. It is an XML based protocol that consists of three
parts: an envelope that defines a framework for describing what is in a message
and how to process it, a set of encoding rules for expressing instances of
application-defined datatypes, and a convention for representing remote
procedure calls and responses.

This project is a follow-on to the Apache SOAP project.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%package manual
Summary:        Manual for %{name}
Group:          Development/Java

%description manual
Documentation for %{name}.

%prep
rm -rf $RPM_BUILD_ROOT
%setup -q -n %{name}-%{archivever}
%patch1 -p1 -b .orig
%patch2 -p1 -b .orig
%patch3 -p1 -b .orig
%patch4

# Remove provided binaries
find . -name "*.jar" -exec rm -f {} \;
find . -name "*.zip" -exec rm -f {} \;
find . -name "*.class" -exec rm -f {} \;

%build

[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java

CLASSPATH=$(build-classpath wsdl4j jakarta-commons-discovery jakarta-commons-httpclient jakarta-commons-logging log4j jaf javamail/mailapi servletapi5)
export CLASSPATH=$CLASSPATH:$(build-classpath oro junit jimi xml-security jsse httpunit jms castor 2>/dev/null)

export OPT_JAR_LIST="ant/ant-nodeps"
%ant -Dcompile.ime=true \
    -Dwsdl4j.jar=$(build-classpath wsdl4j) \
    -Dcommons-discovery.jar=$(build-classpath jakarta-commons-discovery) \
    -Dcommons-logging.jar=$(build-classpath jakarta-commons-logging) \
    -Dcommons-httpclient.jar=$(build-classpath jakarta-commons-httpclient) \
    -Dlog4j-core.jar=$(build-classpath log4j) \
    -Dactivation.jar=$(build-classpath jaf) \
    -Dmailapi.jar=$(build-classpath javamail/mailapi) \
    -Dxerces.jar=$(build-classpath jaxp_parser_impl) \
    -Dservlet.jar=$(build-classpath servletapi5) \
    -Dregexp.jar=$(build-classpath oro 2>/dev/null) \
    -Djunit.jar=$(build-classpath junit 2>/dev/null) \
    -Djimi.jar=$(build-classpath jimi 2>/dev/null) \
    -Djsse.jar=$(build-classpath jsse/jsse 2>/dev/null) \
    clean compile javadocs

%install

### Jar files

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}

pushd build/lib
   install -m 644 axis.jar axis-ant.jar saaj.jar jaxrpc.jar \
           $RPM_BUILD_ROOT%{_javadir}/%{name}
popd

pushd $RPM_BUILD_ROOT%{_javadir}/%{name}
   for jar in *.jar ; do
      vjar=$(echo $jar | sed s+.jar+-%{version}.jar+g)
      mv $jar $vjar
      ln -fs $vjar $jar
   done
popd

### Javadoc

install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr build/javadocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

pushd docs
   rm -fr apiDocs
   ln -fs %{_javadocdir}/%{name} apiDocs
popd

%{__perl} -pi -e 's/\r$//g' LICENSE README release-notes.html changelog.html
find docs -type f -name "*.html" -o -name "*.dbk" -o -name "*.bib" -o -name "*.css" | xargs %{__perl} -pi -e 's/\r$//g'

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi

%files
%defattr(0644,root,root,0755)
%doc LICENSE README release-notes.html changelog.html
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*

%files manual
%defattr(0644,root,root,0755)
%doc docs/*



%define section         free
%define gcj_support     1
%define archivever      1_4

Name:          axis
Version:       1.4
Release:       %mkrel 2.0.7
Epoch:         0
Summary:       SOAP implementation in Java
License:       Apache License
Group:         Development/Java
Url:           http://ws.apache.org/%{name}/
Source0:       %{name}-src-%{archivever}.tar.gz
Patch0:        %{name}-bz152255.patch
Patch1:        %{name}-build.patch
Patch2:        %{name}-imageio.patch
Patch3:        %{name}-objectweb.patch
Patch4:        %{name}-1.4-no-clear-cache.patch
BuildRequires: java-rpmbuild >= 0:1.5
BuildRequires: java-devel
BuildRequires: ant >= 0:1.6
BuildRequires: ant-nodeps
# Mandatory requires
BuildRequires: geronimo-jaf-1.0.2-api
BuildRequires: jakarta-commons-discovery
BuildRequires: jakarta-commons-httpclient >= 0:3.0
BuildRequires: jakarta-commons-logging
BuildRequires: geronimo-javamail-1.3.1-api
BuildRequires: xerces-j2
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
Requires:      geronimo-jaf-1.0.2-api
Requires:      jakarta-commons-discovery
Requires:      jakarta-commons-logging
Requires:      jakarta-commons-httpclient
Requires:      geronimo-javamail-1.3.1-api
Requires:      xerces-j2
Requires:      log4j
Requires:      wsdl4j

%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
BuildRequires:  java-devel
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
%setup -q -n %{name}-%{archivever}
%patch0 -p1
%patch1 -p0
%patch2 -p1
%patch3 -p1
%patch4 -p1
%{__rm} -r docs/apiDocs

# Remove provided binaries
%{_bindir}/find . -name "*.jar" | %{_bindir}/xargs -t %{__rm}
%{_bindir}/find . -name "*.class" | %{_bindir}/xargs -t %{__rm}

%build
CLASSPATH=$(build-classpath wsdl4j jakarta-commons-discovery jakarta-commons-httpclient jakarta-commons-logging log4j jaf javamail servletapi5)
export CLASSPATH=$CLASSPATH:$(build-classpath oro junit jimi xml-security jsse httpunit jms castor 2>/dev/null)
export OPT_JAR_LIST="ant/ant-nodeps"
%{ant} -Dcompile.ime=true -Dnowarn=true \
    -Dwsdl4j.jar=$(build-classpath wsdl4j) \
    -Dcommons-discovery.jar=$(build-classpath jakarta-commons-discovery) \
    -Dcommons-logging.jar=$(build-classpath jakarta-commons-logging) \
    -Dcommons-httpclient.jar=$(build-classpath jakarta-commons-httpclient) \
    -Dlog4j-core.jar=$(build-classpath log4j) \
    -Dactivation.jar=$(build-classpath jaf) \
    -Dmailapi.jar=$(build-classpath javamail) \
    -Dxerces.jar=$(build-classpath jaxp_parser_impl) \
    -Dservlet.jar=$(build-classpath servletapi5) \
    -Dregexp.jar=$(build-classpath oro 2>/dev/null) \
    -Djunit.jar=$(build-classpath junit 2>/dev/null) \
    -Djimi.jar=$(build-classpath jimi 2>/dev/null) \
    -Djsse.jar=$(build-classpath jsse/jsse 2>/dev/null) \
    clean compile

for file in src/org/apache/axis/enum/Scope.java src/org/apache/axis/enum/Style.java src/org/apache/axis/enum/Use.java; do
  %{__mv} ${file} ${file}.bak
done
%{ant} javadocs
for file in src/org/apache/axis/enum/Scope.java src/org/apache/axis/enum/Style.java src/org/apache/axis/enum/Use.java; do
  %{__mv} ${file}.bak ${file}
done

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_javadir}/%{name}

for jar in axis axis-ant saaj jaxrpc; do
   %{__cp} -a build/lib/${jar}.jar %{buildroot}%{_javadir}/%{name}/${jar}-%{version}.jar
done
(cd %{buildroot}%{_javadir}/%{name} && for jar in *-%{version}.jar; do %{__ln_s} ${jar} `echo $jar | %{__sed} "s|-%{version}||g"`; done)

%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a build/javadocs/* %{buildroot}%{_javadocdir}/%{name}-%{version}
(cd %{buildroot}%{_javadocdir} && %{__ln_s} %{name}-%{version} %{name})

pushd docs
   %{__rm} -f apiDocs
   %{__ln_s} %{_javadocdir}/%{name} apiDocs
popd

%{__perl} -pi -e 's/\r$//g' LICENSE README release-notes.html changelog.html docs/svnlog.txt
%{_bindir}/find docs -type f -name "*.html" -o -name "*.dbk" -o -name "*.bib" -o -name "*.css" | %{_bindir}/xargs -t %{__perl} -pi -e 's/\r$//g'

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

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
%dir %{_javadocdir}/%{name}
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*

%files manual
%defattr(0644,root,root,0755)
%doc docs/*



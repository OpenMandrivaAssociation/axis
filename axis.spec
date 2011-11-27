%define section         free
%define archivever      1_4

Name:          axis
Version:       1.4
Release:       5
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
# Build only
Patch5:        %{name}-java16.patch
BuildRequires: jpackage-utils >= 0:1.6
BuildRequires: java-devel >= 0:1.6.0
BuildRequires: ant >= 0:1.6
BuildRequires: ant-nodeps
BuildRequires: ant-junit
BuildRequires: httpunit
BuildRequires: junit
BuildRequires: xmlunit
# Main requires
BuildRequires: bea-stax-api
BuildRequires: bsf
BuildRequires: castor
BuildRequires: javamail
BuildRequires: tomcat6-servlet-2.5-api
BuildRequires: apache-commons-discovery
BuildRequires: jakarta-commons-httpclient >= 0:3.0
BuildRequires: apache-commons-logging
BuildRequires: apache-commons-net
BuildRequires: jakarta-oro
BuildRequires: regexp
BuildRequires: log4j
BuildRequires: wsdl4j
BuildRequires: xalan-j2
BuildRequires: xerces-j2
BuildRequires: xml-commons-apis12
#BuildRequires: xmlbeans
#BuildRequires: xml-security
# optional requires
#BuildRequires: jimi
BuildRequires: jetty
Requires:      java >= 0:1.4.2
Requires:      jpackage-utils >= 0:1.6
Requires:      apache-commons-discovery
Requires:      apache-commons-logging
Requires:      jakarta-commons-httpclient >= 0:3.0
Requires:      javamail
Requires:      log4j
Requires:      wsdl4j
BuildArch:      noarch
Obsoletes:      %{name}14
Provides:       %{name}14 = %version-%release

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
Obsoletes:      %{name}14-javadoc
Provides:       %{name}14-javadoc = %version-%release

%description javadoc
Javadoc for %{name}.

%package manual
Summary:        Manual for %{name}
Group:          Development/Java
Obsoletes:      %{name}14-manual
Provides:       %{name}14-manual = %version-%release

%description manual
Documentation for %{name}.

#--------------------------------------------------------------------

%prep
%setup -q -n %{name}-1_4
ln -s %{_javadocdir}/%{name} docs/apiDocs

# Remove provided binaries
#find . -name "*.jar" -exec rm -f {} \;
for f in $(find . -name "*.jar"); do mv $f $f.no; done
#find . -name "*.zip" -exec rm -f {} \;
for f in $(find . -name "*.zip"); do mv $f $f.no; done
#find . -name "*.class" -exec rm -f {} \;
for f in $(find . -name "*.class"); do mv $f $f.no; done

%patch5 -p0 -b .orig

%build
pushd lib
ln -sf $(build-classpath bea-stax-api) .
ln -sf $(build-classpath bsf) .
ln -sf $(build-classpath castor) .
ln -sf $(build-classpath commons-discovery) .
ln -sf $(build-classpath commons-httpclient) .
ln -sf $(build-classpath commons-logging) .
ln -sf $(build-classpath commons-net) .
ln -sf $(build-classpath httpunit) .
ln -sf $(build-classpath jetty/jetty) .
ln -sf $(build-classpath log4j) .
ln -sf $(build-classpath oro) .
#ln -sf $(build-classpath xml-security) .
#ln -sf $(build-classpath xmlbeans/xbean) .
ln -sf $(build-classpath wsdl4j) .
pushd endorsed
ln -sf $(build-classpath xerces-j2) .
ln -sf $(build-classpath xml-commons-apis12) .
popd
ln -sf $(build-classpath javamail/mail) .
popd

ant \
    -Dant.build.javac.source=1.4 \
    -Dtest.functional.fail=no \
    -Dcommons-discovery.jar=$(build-classpath commons-discovery) \
    -Dcommons-httpclient.jar=$(build-classpath commons-httpclient) \
    -Dcommons-logging.jar=$(build-classpath commons-logging) \
    -Dlog4j-core.jar=$(build-classpath log4j) \
    -Dwsdl4j.jar=$(build-classpath wsdl4j) \
    -Dregexp.jar=$(build-classpath regexp) \
    -Dxmlunit.jar=$(build-classpath xmlunit) \
    -Dmailapi.jar=$(build-classpath javamail/mail) \
    -Dservlet.jar=$(build-classpath servlet) \
    -Dbsf.jar=$(build-classpath bsf) \
    -Dcastor.jar=$(build-classpath castor) \
    -Dcommons-net.jar=$(build-classpath commons-net) \
    -Djetty.jar=$(build-classpath jetty/jetty) \
    -Dsecurity.jar=$(build-classpath xml-security) \
    -Dxmlbeans.jar=$(build-classpath xmlbeans) \
    -Dhttpunit.jar=$(build-classpath httpunit) \
    -Djunit.jar=$(build-classpath junit) \
    clean war javadocs junit

#    -Djimi.jar=$(build-classpath jimi) \

%install
rm -rf $RPM_BUILD_ROOT

### Jar files

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}

pushd build/lib
# install axis-schema.jar when xmlbeans is available
   install -m 644 axis.jar axis-ant.jar saaj.jar jaxrpc.jar \
           $RPM_BUILD_ROOT%{_javadir}/%{name}
popd

### Javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr build/javadocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}-%{version}/webapps
install -m 644 build/axis.war \
    $RPM_BUILD_ROOT%{_datadir}/%{name}-%{version}/webapps

%files
%defattr(-,root,root,-)
%doc LICENSE README release-notes.html changelog.html
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/*.jar
%{_datadir}/%{name}-%{version}

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}

%files manual
%defattr(-,root,root,-)
%doc docs/*



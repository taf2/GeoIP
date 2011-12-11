import Options
from os import popen, unlink, symlink, getcwd
from os import name as platform
from os.path import exists

srcdir = "."
blddir = "build"
VERSION = "0.1"

def set_options(opt):
  opt.tool_options("ar")
  opt.tool_options("compiler_cc")
  opt.tool_options("compiler_cxx")

def test_gettimeofday(conf):
  code = """
    #include <sys/time.h>
    int main(void) {
      struct timeval tp;
      struct timezone tz;
      gettimeofday(&tp, &tz);
      return 0;
    }
  """
  if conf.check_cxx(lib="c", msg="Checking for gettimeofday", fragment=code):
    conf.env.append_value('CPPFLAGS', '-DHAVE_GETTIMEOFDAY=1')

def test_stdint(conf):
  code = """
    #include <stdint.h>
    int main(void) {
      return 0;
    }
  """
  if conf.check_cxx(lib="c", msg="Checking for stdint.h", fragment=code):
    conf.env.append_value('CPPFLAGS', '-DHAVE_STDINT_H=1')

def test_gethostbyname_r(conf):
  code = """
    #include <netdb.h>
    #include <sys/socket.h>
    int main(void) {
      char *tmp;
      int tmplen = 1024;
      struct hostent hostbuf, *hp;
      int herr, hres;
      gethostbyname_r("example.com", &hostbuf, tmp, tmplen, &hp, &herr);
      return 0;
    }
  """
  if conf.check_cxx(lib="c", msg="Checking for gethostbyname_r", fragment=code):
    conf.env.append_value('CPPFLAGS', '-DHAVE_GETHOSTBYNAME_R=1')

def test_vasprintf(conf):
  code = """
    #include <stdarg.h>
    #include <stdio.h>

    static int test_func(const char *str, ...) {
      va_list ap;
      int rc;
      char * f_str;
      va_start(ap, str);
      vasprintf(&f_str, str, ap);
    }

    int main(void) {
      test_func("hello", "x", "y", 0);
      return 0;
    }
  """

  if conf.check_cxx(lib="c", msg="Checking for vasprintf", fragment=code):
    conf.env.append_value('CPPFLAGS', '-DHAVE_VASPRINTF=1')

def test_vsnprintf(conf):
  code = """
    #include <stdarg.h>
    #include <stdio.h>
    #include <stdlib.h>

    static int test_func(const char *str, ...) {
      va_list ap;
      int rc;
      char * f_str;
      va_start(ap, str);
      f_str = (char*)malloc(10);
      vsnprintf(f_str, 10, str, ap);
      free(f_str);
    }

    int main(void) {
      test_func("hello", "x", "y", 0);
      return 0;
    }
  """

  if conf.check_cxx(lib="c", msg="Checking for vsnprintf", fragment=code):
    conf.env.append_value('CPPFLAGS', '-DHAVE_VSNPRINTF=1')

def configure(conf):
  conf.check_tool('compiler_cc')
  conf.check_tool("compiler_cxx")
  conf.check_tool("ar")
  conf.check_tool("node_addon")
  conf.env.append_value('CPPFLAGS', '-DGEOIPDATADIR=\"/usr/local/share/GeoIP\"')
  conf.env.append_value('CPPFLAGS', '-DPACKAGE_NAME=\"GeoIP\"')
  conf.env.append_value('CPPFLAGS', '-DPACKAGE_TARNAME=\"GeoIP\"')
  conf.env.append_value('CPPFLAGS', '-DPACKAGE_VERSION=\"1.4.8\"')
  conf.env.append_value('CPPFLAGS', '-DPACKAGE_STRING=\"GeoIP\ 1.4.8\"')
  conf.env.append_value('CPPFLAGS', '-DPACKAGE_BUGREPORT=\"support@maxmind.com\"')
  conf.env.append_value('CPPFLAGS', '-DPACKAGE_URL=\"\"')

  test_gettimeofday(conf)
  test_stdint(conf)
  test_gethostbyname_r(conf)
  test_vasprintf(conf)
  test_vsnprintf(conf)

def build(bld):
  obj = bld.new_task_gen(features=["cxx", "cc", "cshlib", "node_addon"])
  obj.target = "geoip"
  obj.source = ['src/geoip/GeoIP.c',
                'src/geoip/GeoIPCity.c',
                'src/geoip/GeoIPUpdate.c',
                'src/geoip/md5.c',
                'src/geoip/regionName.c',
                'src/geoip/timeZone.c',
                'src/init.cc', 
                'src/netspeed.cc', 
                'src/country6.cc', 
                'src/country.cc',
                'src/region.cc',
                'src/city6.cc',
                'src/city.cc', 
                'src/org.cc', 
                'src/utils.cc', 
                'src/global.cc']

  obj.lib = []

def link(bld):
  # HACK to get binding.node out of build directory.
  # better way to do this?
  if Options.commands['clean']:
    if exists(getcwd() + '/geoip.node'): unlink('geoip.node')
  else:
    if exists(getcwd() + '/build/default/geoip.node') and not exists(getcwd() + 'geoip.node'):
      symlink(getcwd()+'/build/default/geoip.node', getcwd() + 'geoip.node')

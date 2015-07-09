========
Usage
========

To use sitechantment in a project::

	from sitechantment import SiteCheck

    sc = SiteCheck(verbosity=1, dictfile="./myextrawords")
    sc.check("http://example.com/foo")


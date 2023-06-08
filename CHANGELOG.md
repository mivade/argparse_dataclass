# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-Unreleased]

+ Support for both python 3.6 and 3.7 is removed.
+ Add`TypeError` for non-`Optional` `Union` typing with prompt to use custom 
  `type`
+ Add support for `metavar` in metadata
+ `Literal` types as an alternative for fixed-choice fields
+ Prevent `Literal` and `choices` from being specified at the same time

## [1.0.0] - 2023-01-21

This is the 1.0 release of `argparse_dataclass`.

### Contributors

* @adsharma
* @asasine
* @frank113
* @jayvdb
* @jcal-15
* @mivade
* @rafi-cohen
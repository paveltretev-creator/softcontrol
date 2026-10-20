@ECHO OFF
pushd %~dp0
set SPHINXBUILD=sphinx-build
set SOURCEDIR=.
set BUILDDIR=_build
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end
:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
:end
popd

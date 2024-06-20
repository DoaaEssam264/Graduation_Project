{pkgs}: {
  deps = [
    pkgs.fetchutils
    pkgs.imagemagick6
    pkgs.python39Packages.conda
    pkgs.glibcLocales
  ];
}

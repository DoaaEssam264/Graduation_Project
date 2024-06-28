{pkgs}: {
  deps = [
    pkgs.pgadmin4
    pkgs.fetchutils
    pkgs.imagemagick6
    pkgs.python39Packages.conda
    pkgs.glibcLocales
  ];
}

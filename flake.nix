{
  description = "silly";

  inputs = {
    nixpkgs.url = "nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    sillyORM = {
      url = "github:theverygaming/sillyORM/dev";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      sillyORM,
    }:
    { }
    // flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      rec {
        packages.default = pkgs.python313Packages.buildPythonPackage rec {
          pname = "silly";
          version = "0.0.1";
          pyproject = true;

          build-system = [
            pkgs.python313Packages.setuptools
          ];

          propagatedBuildInputs = with pkgs; [
            sillyORM.packages.${system}.default
            python313Packages.lxml
            python313Packages.starlette
            python313Packages.hypercorn
          ];

          src = ./.;
        };
        devShells.default = pkgs.stdenv.mkDerivation {
          name = "silly";
          buildInputs =
            with pkgs;
            [
              python313

              # lint, fmt, type, docs
              python313Packages.pylint
              python313Packages.mypy
              python313Packages.black
              sphinx
              gnumake

              # test
              python313Packages.coverage
              python313Packages.pytest

              # for convenience
              sqlitebrowser
            ]
            ++ packages.default.propagatedBuildInputs;
        };
      }
    );
}

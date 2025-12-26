{
description = "Jupyter Env using Nix";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: 
    let
      system = "x86_64-linux"; # Adjust for your architecture if needed
      pkgs = import nixpkgs { inherit system; };
      # Adjust which Python packages you want available in Jupyter
      pythonPackages = ps: with ps; [
        ipykernel
        jupyterlab # provides Jupyter Lab
        matplotlib
        networkx # for working with graph data structure
        numpy
      ];
      pythonEnv = pkgs.python3.withPackages pythonPackages;
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pythonEnv
        ];

        shellHook = ''
          echo "Jupyter with Python kernel is ready. Run: 'jupyter lab' to launch."
        '';
      };
    };
}

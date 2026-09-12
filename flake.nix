{
  description = "usdAeco core identity, structure and representation semantics";
  inputs = {
    toolchain.url = "github:criad-com/usdaeco-toolchain?ref=v0.3.10";
    datacentre = { url = "github:criad-com/usdaeco-datacentre?ref=v0.4.8"; flake = false; };
    nixpkgs.follows = "toolchain/nixpkgs";
  };
  outputs = { self, nixpkgs, toolchain, ... }:
    let
      eachSystem = nixpkgs.lib.genAttrs [ "aarch64-darwin" "x86_64-linux" ];
      forSystem = system:
        let
          kit = toolchain.lib.forSystem system;
          pkgs = nixpkgs.legacyPackages.${system};
          
          schema = (kit.buildCodelessSchema { name = "usdAeco"; src = self; deps = [ ]; }).overrideAttrs (old: {
            postInstall = (old.postInstall or "") + ''
              cp -RL tools/usdaeco_core tools/usdaeco_tools "$out/python/"
            '';
          });
          plugins = kit.pluginSet { plugins = [ schema ]; };
          setup = ''
            export TOOLCHAIN_DIR=${toolchain}
            
          '';
          example = pkgs.writeShellApplication {
            name = "example";
            runtimeInputs = [ kit.pythonEnv kit.usd-dev ];
            text = setup + ''
              cp -R ${self} example-work
              chmod -R u+w example-work
              cd example-work
              env -u PYTHONPATH python examples/small_building/run.py "$@"
            '';
          };
          render = pkgs.writeShellApplication {
            name = "render";
            runtimeInputs = [ kit.pythonEnv kit.usd-dev ];
            text = setup + ''
              cp -R ${self} render-work
              chmod -R u+w render-work
              cd render-work
              env -u PYTHONPATH python tools/render_example.py "$@"
            '';
          };
        in { inherit kit pkgs schema plugins setup example render; };
    in {
      packages = eachSystem (system: let p = forSystem system; in {
        default = p.schema;
        pluginSet = p.plugins;
      });
      checks = eachSystem (system: let p = forSystem system; in {
        library = p.pkgs.runCommand "usdAeco-check" { nativeBuildInputs = [ p.kit.pythonEnv p.kit.usd-dev p.pkgs.git ]; }
          (p.setup + ''
            cp -R ${self} source
            chmod -R u+w source
            cd source
            env -u PYTHONPATH python check.py
            env -u PYTHONPATH python -m pytest -q
            mkdir -p "$out"
          '');
        structure = p.pkgs.runCommand "usdAeco-structure" { nativeBuildInputs = [ p.kit.pythonEnv ]; }
          (p.setup + ''
            env -u PYTHONPATH python ${self}/tools/check_structure.py
            mkdir -p "$out"
          '');
      });
      devShells = eachSystem (system: let p = forSystem system; in {
        default = p.pkgs.mkShell {
          packages = [ p.kit.pythonEnv p.kit.usd-dev p.pkgs.git ];
          shellHook = p.setup + "unset PYTHONPATH";
        };
      });
      apps = eachSystem (system: let p = forSystem system; in {
        example = { type = "app"; program = "${p.example}/bin/example"; };
        render = { type = "app"; program = "${p.render}/bin/render"; };
      });
    };
}

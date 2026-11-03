# ModelSim installation and timing replay

ModelSim-Altera Starter Edition 10.1d is installed at `/home/khoale/altera/13.0sp1/modelsim_ase` alongside Quartus II 13.0 SP1. The official installer is `/home/khoale/Downloads/ModelSimSetup-13.0.1.232.run`.

The downloaded installer SHA-1 is `161f55d214e528d6d47b2c5aa872e268b1137e8f`, matching the [vendor download page](https://www.altera.com/downloads/fpga-development-tools/quartus-ii-web-edition-design-software-version-13-0sp1-linux). The user signed in and explicitly authorized accepting the download agreement.

## Linux compatibility

The legacy `bin` launcher selects a nonexistent `linux_rh60` directory on this host. The installed `linuxaloem` executables work when invoked directly, but `vish` also requires the 32-bit ncurses ABI-5 library.

GNU ncurses 6.5 was obtained from `https://ftp.gnu.org/gnu/ncurses/ncurses-6.5.tar.gz` and built locally with:

```bash
./configure --prefix="$HOME/.local/opt/modelsim-compat32" \
  --with-shared --without-normal --without-debug \
  --without-cxx --without-cxx-binding --without-ada \
  --without-progs --without-tests --without-manpages \
  --without-termlib --with-abi-version=5 --disable-widec CC='gcc -m32'
make -j4
make install
```

Source/build logs are under `/home/khoale/.local/src/modelsim-compat`. No system library was replaced. Launchers in `~/.local/bin` invoke the platform-specific tools and set the compatibility library path. `vsim -version` and `vsim -c -do 'quit -f'` both passed.

## Reproduce the timing checks

From the repository root:

```bash
source scripts/modelsim_env.sh
python3 scripts/run_modelsim_timing.py --design temperature_speed
python3 scripts/run_modelsim_timing.py --design temperature_resource
python3 scripts/run_modelsim_timing.py --design weather_speed
python3 scripts/run_modelsim_timing.py --design weather_resource
python3 scripts/audit_delivery.py
```

Starter Edition requires the bundled precompiled `cycloneii_ver` and `altera_ver` libraries for SDF simulation. Compiling the vendor source into `work` is insufficient and produces “SDF files require Altera primitive library.” The runner maps the bundled libraries explicitly.

The test clock remains 20 ns. Original Quartus SDF max delays and timing checks remain enabled. The weather checker observes outputs 9 ns after each rising edge: slow-corner clock-to-output maxima are 8.485 ns (parallel) and 8.070 ns (shared). An earlier 8 ns check sampled unsettled angle bits in the shared design. The temperature checks passed with an 8 ns observation point; future invocations use 9 ns for all designs. A successful run must include both SDF backannotation success and the complete scoreboard PASS, with no timing violations or simulator errors.

A parallel weather timing run terminated with an uncounted-node-locked license lock-file error while another session was active. Future runner invocations are serialized with a user-local file lock to avoid overlapping Starter Edition sessions; this is a precaution, not a bypass of licensing.

Results are recorded in `*_modelsim_timing.json`; the completion audit checks hashes of the actual SDF, netlist, testbench, vectors, and transcript. Physical-board validation is a separate outstanding requirement.

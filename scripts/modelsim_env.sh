# Source this file before invoking ModelSim or the SDF replay runner.
# The platform-specific directory avoids the legacy launcher's Linux detection.
export PATH="$HOME/altera/13.0sp1/modelsim_ase/linuxaloem:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/opt/modelsim-compat32/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra

BIN_DIR = bin
MODELS_DIR = models_cpp

all: $(BIN_DIR)/c_model_basic $(BIN_DIR)/c_model_ridge6

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/c_model_basic: $(MODELS_DIR)/c_model_basic.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/c_model_ridge6: $(MODELS_DIR)/c_model_ridge6.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

clean:
	rm -rf $(BIN_DIR)

.PHONY: all clean

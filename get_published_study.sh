#!/bin/sh
# Clone the published two-cell study at v1.0.0 into external/, where src/ looks for its archived series and its solver.
set -e
mkdir -p external
if [ ! -d external/m50-two-cell-pilot ]; then
  git clone --branch v1.0.0 --depth 1 https://github.com/siddharth161204-wq/m50-two-cell-pilot.git external/m50-two-cell-pilot
fi
git -C external/m50-two-cell-pilot rev-parse HEAD

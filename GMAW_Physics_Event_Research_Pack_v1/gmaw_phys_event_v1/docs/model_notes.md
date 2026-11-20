# Reference model and physical assumptions

These executable models are not the published MBGN source, a reproduction of its
scores, or an exact parameter-count match. They use small independently defined
1D/2D CNNs with no downloaded weights. All variants use the current image;
electrical histories are causal. The snapshot comparator also uses a backward
100 ms window, rather than the paper's centered window.

| Variant | Temporal processing | Explicit extra features | Spatial prior |
| --- | --- | --- | --- |
| snapshot_fusion | Current waveform only | None by default | None |
| history_gru | Unidirectional electrical GRU | None by default | None |
| power_features | Current-image-query content attention | Mean native U*I | None |
| thermal_filter | The same content attention | Mean power and thermal mixture | None |
| phys_align | The same content attention | Mean power and thermal mixture | Gaussian log-prior plus hard support |

The power/thermal/physical-alignment variants have the same pointwise key/value
architecture. They do not pass attention keys through a GRU: otherwise masked
history could re-enter via the hidden state of a valid key. Current image and
condition have their own final fusion branch. Thermal memory before the spatial
support is intentional: it is a physical state, not cross-token electrical
attention leakage. Only current and past inputs are available to the model.

## Thermal state

For a fixed positive time constant, the normalized proxy satisfies
`dz/dt = (P/P_ref - z)/tau`. Its exact piecewise-constant-power update is a convex
combination of the previous state and the current normalized input. Nonnegative
power therefore keeps the state nonnegative; zero power causes exponential
decay. The data loader must integrate the bank once per continuous segment and
then slice windows. The first bin has zero duration and uses the manifest's
initial power; a warm-up exclusion reduces dependence on that assumed initial
state. Power-bin means must be computed from native U*I samples, not products of
independent means. Gaps in acquisition must be handled upstream, not bridged
without justification.

The model learns one global softmax mixture of the fixed bank. This avoids free
per-sample efficiency/state-scale factors, but it does not make the resulting
state a temperature or prove unique identification of physical parameters. The
configured time constants are design assumptions, without thermal calibration.
Select them only using training/validation data. A fixed low-pass filter bank
is not itself a novel physical law or an ARX baseline.

## Alignment and auxiliary target

The alignment support and Gaussian prior use measured trajectory, camera view
offset, and position uncertainty. They never use RT event positions, labels, or
future geometry. Support-free samples must be skipped. With physical alignment
enabled, attention is exactly zero outside support. With it disabled, the same
architecture uses content attention over all already acquired history.

`use_heat`, `use_alignment`, and `use_aux` are explicit flags. Disable inherited
flags when configuring baselines. `use_aux=False` removes the geometry head and
returns a zero placeholder of shape `[B,3]`; the trainer must not score that
placeholder as a geometric prediction. With auxiliary training enabled, the
sigmoid head predicts three normalized ROI geometry fractions. These are not
millimetres or temperature. Future geometry is a loss target only and is never
read by `forward`. Predictions remain available when auxiliary observations are
missing. Report both parameter counts and the extra-supervision difference when
comparing an auxiliary-trained model with classification-only baselines.

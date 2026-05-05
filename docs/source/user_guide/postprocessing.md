(user_guide/postprocessing)=
# Postprocessing

After Suite2p extracts fluorescence traces, `photon-mosaic` runs two post-Suite2p stages on each session: **neuropil correction** and **dF/F calculation**. Both run automatically as part of the workflow; their parameters are exposed in `config.yaml`.

The output layout for one session is:

```
derivatives/sub-*/ses-*/funcimg/
├── suite2p/plane0/{F.npy, Fneu.npy, ...}   # from Suite2p
├── neuropil/plane0/Fc.npy                   # neuropil correction
└── dff/plane0/dFF.npy                       # dF/F traces
```

## Neuropil correction

Implemented by the `neuropil` rule (`photon_mosaic/workflow/neuropil.smk`), which calls `calculate_neuropil_correction` in `photon_mosaic/rules/neuropil_run.py`.

- **Inputs:** `suite2p/plane0/F.npy`, `suite2p/plane0/Fneu.npy`
- **Output:** `neuropil/plane0/Fc.npy`
- **Formula:** `Fc = F - neucoeff * (Fneu - median(Fneu))`

The median is computed per neuropil trace, so the correction subtracts the modulation of the neuropil signal rather than its absolute level.

### Configuration

```yaml
neuropil_ops:
  neucoeff: 0.7   # weight applied to the demedianed neuropil trace
```

`neucoeff = 0.7` is the standard default in the Suite2p / Pachitariu et al. literature. Lower values trust the raw `F` more; higher values subtract more neuropil contamination.

## dF/F calculation

Implemented by the `dff` rule (`photon_mosaic/workflow/dff.smk`), which calls `calculate_dFF` in `photon_mosaic/rules/dff_run.py`.

- **Input:** `neuropil/plane0/Fc.npy` (from the previous stage)
- **Output:** `dff/plane0/dFF.npy`

For each cell, baseline fluorescence `F0` is estimated by fitting a Gaussian Mixture Model to the neuropil-corrected trace and taking the mean of the lowest-mean component. `dF/F` is then computed in the standard way as `(Fc - F0) / F0`.

### Configuration

```yaml
dff_ops:
  gmm_ncomponents: 2   # number of GMM components used to estimate F0
```

Two components is the typical choice (one for "baseline" frames, one for "active" frames). Increasing this can help on cells with multiple modes of activity but adds parameters and risks overfitting on short recordings.

## Order of execution

Snakemake resolves dependencies automatically: `dff` requires `neuropil`'s output, which requires `suite2p`'s output. Running `photon-mosaic` produces all three. To re-run only one stage, use `--forcerun`:

```bash
photon-mosaic --forcerun neuropil    # re-run neuropil + dff (downstream)
photon-mosaic --forcerun dff         # re-run only dff
```

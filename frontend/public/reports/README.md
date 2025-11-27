Place your PDF reports in this directory so the frontend can serve them statically.

Expected filenames:
- `ocr_results.pdf`
- `psnr_ssim_results.pdf`

After adding the files, the Metrics page will load them at:
- `/reports/ocr_results.pdf`
- `/reports/psnr_ssim_results.pdf`

If you prefer a different path or filenames, update `frontend/src/pages/Metrics.jsx` accordingly.

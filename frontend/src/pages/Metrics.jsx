import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Metrics.css';

const PDFViewer = ({ src }) => (
  <div className="pdf-wrap">
    <iframe title={src} src={src} frameBorder="0" className="pdf-frame" />
  </div>
);

const Metrics = () => {
  const [active, setActive] = useState('ocr');
  const navigate = useNavigate();

  const reportsBase = '/reports';

  return (
    <div className="metrics-page">
      <header className="metrics-header">
        <button className="back-btn" onClick={() => navigate('/dashboard')}>← Back</button>
        <h2>Model Metrics & Reports</h2>
      </header>

      <div className="metrics-controls">
        <button className={active === 'ocr' ? 'active' : ''} onClick={() => setActive('ocr')}>OCR Results</button>
        <button className={active === 'psnr' ? 'active' : ''} onClick={() => setActive('psnr')}>PSNR & SSIM</button>
      </div>

      <div className="metrics-viewer">
        {active === 'ocr' && <PDFViewer src={`${reportsBase}/ocr_results.pdf`} />}
        {active === 'psnr' && <PDFViewer src={`${reportsBase}/psnr_ssim_results.pdf`} />}
      </div>

      <div className="metrics-note">
        <p>If the PDFs don't load, make sure the files are placed in <code>frontend/public/reports/</code> and named <code>ocr_results.pdf</code> and <code>psnr_ssim_results.pdf</code>.</p>
      </div>
    </div>
  );
};

export default Metrics;

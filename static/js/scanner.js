document.addEventListener('DOMContentLoaded', () => {
  const btnCamera = document.getElementById('btn-camera');
  const scanFrame = document.getElementById('scan-frame');
  const placeholder = document.getElementById('frame-placeholder');
  const video = document.getElementById('camera-feed');
  const canvas = document.getElementById('camera-canvas');
  const cameraImageInput = document.getElementById('camera_image');
  const imgInput = document.getElementById('img-input');
  const form = document.getElementById('scan-form');

  let stream = null;
  let captureMode = false;

  // Show chosen filename feedback
  if (imgInput) {
    imgInput.addEventListener('change', () => {
      if (imgInput.files.length > 0) {
        stopCamera();
        if (placeholder) {
          placeholder.innerHTML = '// FILE READY —<br>' + imgInput.files[0].name;
        }
      }
    });
  }

  if (btnCamera && video) {
    btnCamera.addEventListener('click', async () => {
      if (!captureMode) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
          video.srcObject = stream;
          video.style.display = 'block';
          if (placeholder) placeholder.style.display = 'none';
          btnCamera.textContent = 'Capture Frame';
          captureMode = true;
        } catch (err) {
          if (placeholder) placeholder.textContent = '// CAMERA UNAVAILABLE — use file upload instead';
        }
      } else {
        // Capture current frame
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        cameraImageInput.value = dataUrl;

        video.style.display = 'none';
        const img = document.createElement('img');
        img.src = dataUrl;
        scanFrame.insertBefore(img, scanFrame.firstChild);

        stopCamera();
        btnCamera.textContent = 'Use Camera';
        captureMode = false;
      }
    });
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
  }

  // Sweep scanline while the form is submitting (analysis in progress)
  if (form) {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.textContent = 'Analyzing...';
        submitBtn.disabled = true;
      }
    });
  }

  // Reveal existing scanline (on result page) with a brief sweep then fade
  const scanline = document.getElementById('scanline');
  if (scanline) {
    scanline.style.display = 'block';
    setTimeout(() => { scanline.style.opacity = '0'; }, 1800);
  }
});

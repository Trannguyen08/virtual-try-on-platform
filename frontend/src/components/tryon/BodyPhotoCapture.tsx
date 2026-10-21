import React, { useEffect, useRef, useState } from 'react';

/** Photos stay in this page; the current body API accepts measurements only. */
export function BodyPhotoCapture({ active = true }: { active?: boolean }) {
  const [photo, setPhoto] = useState<Blob | null>(null);
  const [preview, setPreview] = useState('');
  const [cameraOpen, setCameraOpen] = useState(false);
  const [error, setError] = useState('');
  const video = useRef<HTMLVideoElement>(null);

  useEffect(() => { if (!active) setCameraOpen(false); }, [active]);

  useEffect(() => {
    if (!photo) return;
    const url = URL.createObjectURL(photo);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [photo]);

  useEffect(() => {
    if (!cameraOpen) return;
    let disposed = false;
    let stream: MediaStream | null = null;
    if (!navigator.mediaDevices?.getUserMedia) {
      setError('Camera cần HTTPS hoặc localhost. Bạn có thể chọn ảnh từ thiết bị.');
      setCameraOpen(false);
      return;
    }
    void navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
      .then((received) => {
        if (disposed) { received.getTracks().forEach((track) => track.stop()); return; }
        stream = received;
        if (video.current) video.current.srcObject = stream;
      }).catch(() => {
        if (!disposed) {
          setError('Không mở được camera. Cho phép truy cập camera hoặc chọn ảnh từ thiết bị.');
          setCameraOpen(false);
        }
      });
    return () => {
      disposed = true;
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, [cameraOpen]);

  const capture = () => {
    const source = video.current;
    if (!source?.videoWidth) { setError('Camera chưa sẵn sàng. Vui lòng chờ một chút.'); return; }
    const canvas = document.createElement('canvas');
    canvas.width = source.videoWidth;
    canvas.height = source.videoHeight;
    const context = canvas.getContext('2d');
    if (!context) return;
    context.drawImage(source, 0, 0);
    canvas.toBlob((blob) => {
      if (blob) { setPhoto(blob); setCameraOpen(false); setError(''); }
    }, 'image/jpeg', 0.9);
  };

  return <section className="outfit-photo" aria-label="Ảnh cá nhân">
    <span className="outfit-eyebrow">ẢNH CỦA BẠN</span>
    <h3>Chụp ảnh, tạo model của bạn</h3>
    {cameraOpen ? <video ref={video} autoPlay playsInline muted aria-label="Camera xem trước" />
      : preview ? <img src={preview} alt="Ảnh cá nhân đã chọn" />
        : <div className="outfit-photo-placeholder"><span aria-hidden="true">◎</span><p>Ảnh toàn thân, đứng thẳng<br />và đủ sáng</p></div>}
    <div className="outfit-actions">
      {cameraOpen ? <>
        <button type="button" className="outfit-primary" onClick={capture}>Chụp ảnh</button>
        <button type="button" onClick={() => setCameraOpen(false)}>Đóng camera</button>
      </> : <button type="button" onClick={() => { setError(''); setCameraOpen(true); }}>Mở camera</button>}
      <label className="outfit-file-button">Chọn ảnh
        <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(event) => {
          const file = event.target.files?.[0];
          event.target.value = '';
          if (!file) return;
          if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 10 * 1024 * 1024) {
            setError('Chọn ảnh JPEG, PNG hoặc WebP tối đa 10 MiB.'); return;
          }
          setPhoto(file); setCameraOpen(false); setError('');
        }} />
      </label>
    </div>
    {error && <p role="alert" className="outfit-error">{error}</p>}
    <p className="outfit-note">Ảnh chỉ xem trước trong phiên này. Model 3D hiện được dựng từ thông số bên cạnh, chưa tái dựng hình thể từ ảnh.</p>
  </section>;
}

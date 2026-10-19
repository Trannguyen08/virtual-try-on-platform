import React, { ChangeEvent, DragEvent, useEffect, useMemo, useRef } from 'react';
import { GarmentView } from '../api/garment3d';

export type GarmentFiles = Partial<Record<GarmentView, File>>;

interface Props {
  files: GarmentFiles;
  onChange: (next: GarmentFiles) => void;
  disabled?: boolean;
  tryOnImagesOnly?: boolean;
}

const SLOTS: Array<{ view: GarmentView; label: string; required?: boolean }> = [
  { view: 'front', label: 'Mặt trước', required: true },
  { view: 'left', label: 'Bên trái' },
  { view: 'back', label: 'Mặt sau' },
  { view: 'right', label: 'Bên phải' },
];

function ViewSlot({
  view,
  label,
  required,
  file,
  disabled,
  tryOnImagesOnly,
  onFile,
}: {
  view: GarmentView;
  label: string;
  required?: boolean;
  file?: File;
  disabled?: boolean;
  tryOnImagesOnly?: boolean;
  onFile: (file?: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const preview = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(
    () => () => {
      if (preview) URL.revokeObjectURL(preview);
    },
    [preview],
  );

  const select = (event: ChangeEvent<HTMLInputElement>) => onFile(event.target.files?.[0]);
  const drop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    if (disabled) return;
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) onFile(dropped);
  };
  const remove = () => {
    if (inputRef.current) inputRef.current.value = '';
    onFile(undefined);
  };
  return (
    <article className={`g3d-upload-card${file ? ' g3d-upload-card--selected' : ''}`}>
      <div className="g3d-upload-card__heading">
        <span>{label}</span>
        <span className={required ? 'g3d-badge g3d-badge--required' : 'g3d-badge'}>
          {required ? 'Bắt buộc' : 'Tùy chọn'}
        </span>
      </div>
      <label
        htmlFor={`garment-${view}`}
        className="g3d-upload-card__dropzone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={drop}
      >
        {preview ? (
          <img
            src={preview}
            alt={`Ảnh ${label.toLowerCase()}`}
            className="g3d-upload-card__preview"
          />
        ) : (
          <div className="g3d-upload-card__empty">
            <span className="g3d-upload-card__icon" aria-hidden="true">+</span>
            <strong>Chọn hoặc kéo ảnh {label.toLowerCase()} vào đây</strong>
            <small>{tryOnImagesOnly ? 'JPEG, PNG hoặc WebP' : 'JPEG, PNG, WebP hoặc BMP'}</small>
          </div>
        )}
      </label>
      <input
        ref={inputRef}
        id={`garment-${view}`}
        className="g3d-visually-hidden"
        type="file"
        accept={tryOnImagesOnly
          ? 'image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp'
          : 'image/jpeg,image/png,image/webp,image/bmp,.jpg,.jpeg,.png,.webp,.bmp'}
        disabled={disabled}
        onChange={select}
      />
      <div className="g3d-upload-card__footer">
        <span className="g3d-upload-card__filename" title={file?.name}>
          {file?.name ?? 'Chưa chọn ảnh'}
        </span>
        {file && (
          <button
            className="g3d-button g3d-button--danger g3d-button--small"
            type="button"
            disabled={disabled}
            onClick={remove}
          >
            Xóa
          </button>
        )}
      </div>
    </article>
  );
}

export const GarmentImageInputs: React.FC<Props> = ({ files, onChange, disabled, tryOnImagesOnly }) => (
  <section className="g3d-panel" aria-labelledby="garment-images-title">
    <div className="g3d-section-heading">
      <div>
        <span className="g3d-eyebrow">Bước 1</span>
        <h2 id="garment-images-title">Ảnh cùng một trang phục</h2>
      </div>
      <span className="g3d-view-count">
        {Object.values(files).filter(Boolean).length}/4 góc
      </span>
    </div>
    <p className="g3d-section-copy">
      Mặt trước là bắt buộc. Các góc còn lại giúp tái tạo mặt sau và độ dày chính xác hơn.
    </p>
    <div className="g3d-notice">
      <span aria-hidden="true">✓</span>
      <p>{tryOnImagesOnly
        ? 'Mỗi ảnh tối đa 10 MiB và 16 triệu pixel. Hệ thống kiểm tra nội dung ảnh trước khi tạo job.'
        : 'Hệ thống giữ nguyên tỉ lệ, căn giữa và chuẩn hóa ảnh thành 1024×1024 trước khi phân tích.'}
      </p>
    </div>
    <div className="g3d-upload-grid">
      {SLOTS.map((slot) => (
        <ViewSlot
          key={slot.view}
          {...slot}
          file={files[slot.view]}
          disabled={disabled}
          tryOnImagesOnly={tryOnImagesOnly}
          onFile={(file) => onChange({ ...files, [slot.view]: file })}
        />
      ))}
    </div>
  </section>
);

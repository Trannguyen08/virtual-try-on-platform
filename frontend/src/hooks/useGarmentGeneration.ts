import { useCallback, useEffect, useRef, useState } from 'react';
import {
  createGarmentGeneration,
  Garment3DGeneration,
  Garment3DJob,
  GarmentImageSet,
  getGarmentGeneration,
  getGarmentJob,
} from '../api/garment3d';

const TERMINAL_STATES = new Set(['completed', 'failed', 'cancelled']);

export function useGarmentGeneration() {
  const [job, setJob] = useState<Garment3DJob | null>(null);
  const [generation, setGeneration] = useState<Garment3DGeneration | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const timerRef = useRef<number | null>(null);

  const stop = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    if (timerRef.current !== null) window.clearTimeout(timerRef.current);
    timerRef.current = null;
  }, []);

  useEffect(() => stop, [stop]);

  const poll = useCallback(
    async (jobId: string, startedAt: number) => {
      const controller = new AbortController();
      abortRef.current = controller;
      try {
        const nextJob = await getGarmentJob(jobId, controller.signal);
        setJob(nextJob);
        if (nextJob.status === 'completed') {
          const result = await getGarmentGeneration(nextJob.generation_id, controller.signal);
          setGeneration(result);
          return;
        }
        if (TERMINAL_STATES.has(nextJob.status)) {
          setError(nextJob.error?.message ?? 'Không thể tạo mô hình 3D.');
          return;
        }
        const delay = Date.now() - startedAt > 60_000 ? 5_000 : 3_000;
        timerRef.current = window.setTimeout(() => void poll(jobId, startedAt), delay);
      } catch (reason) {
        if (controller.signal.aborted) return;
        setError(reason instanceof Error ? reason.message : 'Không thể kiểm tra tiến trình.');
      }
    },
    [],
  );

  const submit = useCallback(
    async (images: GarmentImageSet) => {
      stop();
      setSubmitting(true);
      setError(null);
      setJob(null);
      setGeneration(null);
      const controller = new AbortController();
      abortRef.current = controller;
      try {
        const created = await createGarmentGeneration(images, controller.signal);
        await poll(created.job_id, Date.now());
      } catch (reason) {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : 'Không thể gửi ảnh.');
        }
      } finally {
        setSubmitting(false);
      }
    },
    [poll, stop],
  );

  const reset = useCallback(() => {
    stop();
    setJob(null);
    setGeneration(null);
    setError(null);
    setSubmitting(false);
  }, [stop]);

  return { job, generation, error, submitting, submit, reset };
}

import { useEffect, useMemo, useRef, useState } from "react";
import { Camera, LoaderCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { recognize, type RecognitionResult } from "@/lib/api";

type Props = {
  onRecognition: (result: RecognitionResult) => void;
};

const POLL_INTERVAL_MS = 1500;

export function CameraPanel({ onRecognition }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const sessionId = useMemo(
    () => `session-${Math.random().toString(36).slice(2)}-${Date.now()}`,
    []
  );

  useEffect(() => {
    return () => {
      const stream = videoRef.current?.srcObject;
      if (stream instanceof MediaStream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    if (!isStreaming) {
      return;
    }

    const timer = window.setInterval(async () => {
      if (!videoRef.current || !canvasRef.current || isSending) {
        return;
      }

      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (!video.videoWidth || !video.videoHeight) {
        return;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext("2d");
      if (!context) {
        return;
      }

      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      setIsSending(true);
      try {
        const frame = canvas.toDataURL("image/jpeg", 0.8);
        const result = await recognize(frame, sessionId);
        onRecognition(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to reach the backend.");
      } finally {
        setIsSending(false);
      }
    }, POLL_INTERVAL_MS);

    return () => window.clearInterval(timer);
  }, [isSending, isStreaming, onRecognition, sessionId]);

  async function startCamera() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsStreaming(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Camera access was denied.");
    }
  }

  function stopCamera() {
    const stream = videoRef.current?.srcObject;
    if (stream instanceof MediaStream) {
      stream.getTracks().forEach((track) => track.stop());
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  }

  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-black/5 bg-white/90 px-6 py-5">
        <p className="text-xs uppercase tracking-[0.28em] text-slateblue">Live Feed</p>
        <h2 className="mt-2 text-2xl font-semibold">Camera Recognition Loop</h2>
      </div>
      <div className="p-6">
        <div className="relative overflow-hidden rounded-[24px] bg-ink">
          <video ref={videoRef} className="aspect-video w-full object-cover" muted playsInline />
          <canvas ref={canvasRef} className="hidden" />
          <div className="pointer-events-none absolute left-4 top-4 rounded-full bg-white/90 px-3 py-2 text-xs font-medium text-ink">
            Blink once to trigger attendance.
          </div>
          <div className="pointer-events-none absolute inset-x-10 inset-y-10 rounded-[28px] border-2 border-dashed border-white/50" />
          {isSending ? (
            <div className="absolute bottom-4 right-4 inline-flex items-center gap-2 rounded-full bg-white/90 px-3 py-2 text-xs font-medium text-ink">
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Sending frame
            </div>
          ) : null}
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          {!isStreaming ? (
            <Button onClick={startCamera}>
              <Camera className="mr-2 h-4 w-4" />
              Start Camera
            </Button>
          ) : (
            <Button onClick={stopCamera} variant="secondary">
              Stop Camera
            </Button>
          )}
        </div>

        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
      </div>
    </Card>
  );
}

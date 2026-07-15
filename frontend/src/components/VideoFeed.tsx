import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getVideoStreamUrl } from "@/lib/api";

interface VideoFeedProps {
  /** Whether streaming should be attempted. */
  active: boolean;
}

/**
 * Render the live MJPEG video stream from the robot camera.
 *
 * This uses an iframe pointing directly at the robot bridge stream endpoint.
 * Because the stream already works stand-alone in a browser tab, embedding it
 * as a nested document is the quickest reliable way to show it in the dashboard
 * without fighting CORS or proxy buffering.
 */
export function VideoFeed({ active }: VideoFeedProps) {
  const streamUrl = getVideoStreamUrl();

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Video Feed</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {active ? (
          <iframe
            src={streamUrl}
            title="Robot camera feed"
            className="block aspect-video w-full border-0"
            allow="autoplay"
            sandbox="allow-same-origin allow-scripts"
          />
        ) : (
          <div className="flex aspect-video w-full items-center justify-center bg-muted text-sm text-muted-foreground">
            Video stream is paused
          </div>
        )}
      </CardContent>
    </Card>
  );
}

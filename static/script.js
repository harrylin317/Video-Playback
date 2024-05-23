document.addEventListener("DOMContentLoaded", function () {
  const video = document.getElementById("myVideo");

  // List of segments with start, end, and speed ratio from the template context
  const segments = JSON.parse(
    document.getElementById("segments-data").textContent
  );

  video.addEventListener("timeupdate", function () {
    const currentTime = video.currentTime;

    // Find the current segment based on the current time
    const currentSegment = segments.find(
      (segment) => currentTime >= segment[0] && currentTime < segment[1]
    );

    if (currentSegment) {
      // Set the playback rate to the segment's speed
      video.playbackRate = currentSegment[2];
    } else {
      // Set the playback rate to normal if not in any segment
      video.playbackRate = 1.0;
    }
  });
});

var video = videojs("my-video");

var markers = [
  { time: 50, label: "Hello" },
  { time: 150, label: "Hello asd a asd asdsad" },
  { time: 200, label: "Hello" },
  { time: 220, label: "Hello" },
];

video.on("loadedmetadata", function () {
  var total = video.duration();

  var p = jQuery(video.controlBar.progressControl.children_[0].el_);

  for (var i = 0; i < markers.length; i++) {
    var left = (markers[i].time / total) * 100 + "%";

    var time = markers[i].time;

    var el = jQuery(
      '<div class="vjs-marker" style="left:' +
        left +
        '" data-time="' +
        time +
        '"><span>' +
        markers[i].label +
        "</span></div>"
    );
    el.click(function () {
      video.currentTime($(this).data("time"));
    });

    p.append(el);
  }
});

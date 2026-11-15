const select = document.getElementById("search-engine");
const status = document.getElementById("status");

new QWebChannel(qt.webChannelTransport, function (channel) {
    const settings = channel.objects.settings;

    settings.getSearchEngine(function (engine) {
        select.value = engine;
        select.disabled = false;
    });

    select.addEventListener("change", function () {
        settings.setSearchEngine(select.value, function (success) {
            status.textContent = success
                ? "Updated for this session."
                : "Could not update settings.";
        });
    });
});

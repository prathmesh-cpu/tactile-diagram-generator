function selectTextFile() {
    var fileInput = document.getElementById("fileInput");
    fileInput.click();
}

function handleFileSelect(event) {
    var file = event.target.files[0];
    var reader = new FileReader();

    reader.onload = function (e) {
        var fileContent = e.target.result;
        document.getElementById("textInput").value = fileContent;
    };

    reader.readAsText(file);
}

document.getElementById("fileInput").addEventListener("change", handleFileSelect, false);

function convertToBraille() {
    var textInput = document.getElementById("textInput").value;
    var brailleOutput = document.getElementById("brailleOutput");
    var brailleText = "";

    var brailleMap = {
        a: "⠁",
        b: "⠃",
        c: "⠉",
        d: "⠙",
        e: "⠑",
        f: "⠋",
        g: "⠛",
        h: "⠓",
        i: "⠊",
        j: "⠚",
        k: "⠅",
        l: "⠇",
        m: "⠍",
        n: "⠝",
        o: "⠕",
        p: "⠏",
        q: "⠟",
        r: "⠗",
        s: "⠎",
        t: "⠞",
        u: "⠥",
        v: "⠧",
        w: "⠺",
        x: "⠭",
        y: "⠽",
        z: "⠵",
        " ": "⠀"
    };

    for (var i = 0; i < textInput.length; i++) {
        var char = textInput[i].toLowerCase();
        if (brailleMap[char]) {
            brailleText += brailleMap[char] + " ";
        }
    }

    brailleOutput.textContent = brailleText;
}

function downloadAsImage() {
    var brailleOutput = document.getElementById("brailleOutput");
    html2canvas(brailleOutput).then(function (canvas) {
        var image = canvas.toDataURL("image/png");

        var link = document.createElement("a");
        link.href = image;
        link.download = "braille_output.png"; 

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}
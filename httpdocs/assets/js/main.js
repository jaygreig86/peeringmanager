window.addEventListener("load", function(){
    fetch('/content.php?function=ackalerts').catch(_ => 'Error acknowledging alerts')
});
const confirmAndRequest = (message, url, method) => {
    if (confirm(message)) {
        if (method.toLowerCase() === "get") {
            fetch(url, { method: "GET" })
                //.then(_ => location.reload())
        } else if (method.toLowerCase() === "post") {
            fetch(url, { method: "POST" })
                //.then(_ => location.reload())
        } else {
            console.log(`Unknown method ${method}`)
        }
    }
}
const isVisible = (node) => {
    return !!( node.offsetWidth || node.offsetHeight || node.getClientRects().length );
}
const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
        .catch(err => {
            alert('Error copying text to clipboard: '+ err)
        })
}
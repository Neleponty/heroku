function getTop(bottom,top, $div,name) {
    $.ajax({
        "method": "Get",
        "url": name + "topList?bottom="+bottom + "&top=" +top ,
        success : $div.html(response.content)
})
}



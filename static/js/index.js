var arr=[1,2,3,]
console.log(typeof(arr))

$(".btn_box").on("click",function(){
    $(".info_medicine_title").html("")
    $(".info_list").html("")
    inputValue=$(".input_box>input").val()
    if(!inputValue){
        alert("请输入内容")
        return
    }
    $.get("searchMedicine", { name: inputValue},
        function(result){
        result=JSON.parse(result);
        console.log(result.length)
        if(result.length == 0)
        {
            errorInfo = "查找失败"
            html="<li>"+ errorInfo +"</li>"
            $(".info_list").append(html)
            return
        }
		for (index in result)
		{
            ret = result[index]
            title = ret["title"]
            path = ret["path"]
            console.log(title,path)
            html = "<a href=" + path + ">" + title + "</a><br> "
            $(".info_list").append(html)
        }
        });
})



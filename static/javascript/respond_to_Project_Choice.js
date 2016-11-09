function getSuperVisorFromChoice(){
    var ProjName   = document.getElementById("id_projectName");
    var SuperVisor = document.getElementById("id_Supervisor");
    var SceneEle   = document.getElementById("id_sceneName");

	var selectedOption = function(){
		return SceneEle.options[SceneEle.selectedIndex].value;
	};
    var selectedName = selectedOption();
	django.jQuery.getJSON('/get_project_Supervisor/' + selectedName , function(ret){
		for (var i = ret.length - 1; i >= 0; i--) {
            ProjName.value  =ret[i]['projname'];
            SuperVisor.value=ret[i]['supervisor'];
            console.log(ret[i]['supervisor']);
            break
        }
    });
}
function adjustOptionForSubPath(rootpath){
	var RawPlatesPath = document.getElementById('id_RawPlatesPath');
	var AssetsPath = document.getElementById('id_AssetsPath');
	var VFXPath = document.getElementById('id_VFXPath');
	var DailyPath = document.getElementById('id_DailyPath');
	var EditPath = document.getElementById('id_EditPath');
    var ProjRootPath = document.getElementById('id_ProjRootPath');

	var selectedOption = function(){
		return ProjRootPath.options[ProjRootPath.selectedIndex].value;
	};
	console.log(selectedOption());
	// console.log(ProjRootPath.selectedIndex);
	var selectedRootPath = selectedOption();
	django.jQuery.getJSON('/getSubPath/' + selectedRootPath , function(ret){
		for (var i = ret.length - 1; i >= 0; i--) {
			// Set Rawplate Pate.
			rawplate_path = ret[i]['RawPlatesPath'];
			RawPlatesPath.setAttribute('value',rawplate_path);

			assets_path = ret[i]['AssetsPath'];
			AssetsPath.setAttribute('value',assets_path);

			vfx_path = ret[i]['VFXPath']
			VFXPath.setAttribute('value',vfx_path);

			daily_path = ret[i]['DailyPath'];
			DailyPath.setAttribute('value',daily_path);

			edit_path = ret[i]['EditPath'];
			EditPath.setAttribute('value',edit_path);
		};
	});
}

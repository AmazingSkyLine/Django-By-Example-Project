(function()
{
	var name = document.getElementById('personaName');
	if(name.value!=='隐血空夜')
	{
		name.value = '隐血空夜';
		var button = document.getElementsByClassName('btn_green_white_innerfade btn_medium')[0];
		button.click();
	}
})();
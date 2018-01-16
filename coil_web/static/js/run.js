/* 
 * run.js 
 * 
 * supports js ops of templates/pages/run.html
 */ 

// 
function mccoil_select() { 
    // flip hidden input in form for mccoil selection 
    var mccoil_input = document.getElementById("mccoil_selected_input");
    if (mccoil_input.value == "checked") 
	mccoil_input.value = "unchecked";
    else 
	mccoil_input.value = "checked"; 
    console.log("Changed mccoil_selected_input to " + mccoil_input.value); 
    return; 
} 
  
// to handle radio input
function add_maf_select(selected) {
    // remove maf_select element, if already there
    var maf_select = document.getElementById("maf_select_li");
    if (maf_select != null) {
        maf_select.parentNode.removeChild(maf_select);
	console.log("maf_select_li was removed."); 
    } else { 
	console.log("maf_select_li was not found."); 
    } 
    maf_select = document.createElement("li"); 
    maf_select.id = "maf_select_li";
    maf_select.className = "list-group-item";
    // create maf_select element and add to form
    if (selected == "data") {
        var t = document.createTextNode("Great, MAFs will be estimated from the data.");
        maf_select.appendChild(t); 
    } else if (selected == "file") {
        // add file upload
	maf_select_file_label = document.createElement("label");
	maf_select_file_label.className = "btn btn-default btn-file";
	var t = document.createTextNode("Choose MAFs File");
	maf_select_file_label.appendChild(t); 
	maf_select_file = document.createElement("input"); 
        maf_select_file.name = "mafs"; 
        maf_select_file.type = "file"; 
	maf_select_file.id = "maf_select";
	maf_select_file.style = "display: none"; 
	maf_select_file_label.appendChild(maf_select_file);
	maf_select.appendChild(maf_select_file_label); 
	console.log("Added maf_select_file to maf_select_li.")
    } else if (selected == "pf3k") {
	maf_select.className = maf_select.className + " clearfix";
	maf_select_pf3k_col1 = document.createElement("div");
	maf_select_pf3k_col1.className = "form-group col-md-2";
        maf_select_geo = document.createElement("select"); 
        maf_select_geo.name = "maf_geo_select";
        maf_select_geo.className = "form-control"; 
	var text;
        var option;
        var options = [["","Choose Geography"],["all","All"],["region","--Region--"],["west_africa","West Africa"],
                       ["central_africa","Central Africa"],["southeast_asia","Southeast Asia"],
                       ["country","--Country--"],["ghana","Ghana"],["bangladesh","Bangladesh"],
                       ["myanmar","Myanmar"],["guinea","Guinea"],["laos","Laos"],["senegal","Senegal"],
                       ["cambodia","Cambodia"],["congo","DR of the Congo"],["gambia","The Gambia"],
                       ["vietnam","Vietnam"],["mali","Mali"],["thailand","Thailand"],["nigeria","Nigeria"],
                       ["malawi","Malawi"]];
        for (var i = 0; i < options.length; i++) {
            option = document.createElement("option");
            if (options[i][0] == "") {
                option.selected = true;
                option.disabled = true;
            } else if (options[i][0] == "region" || options[i][0] == "country") {
                option.disabled = true;
            }
            option.value = options[i][0];
            text = document.createTextNode(options[i][1]);
            option.appendChild(text);
            maf_select_geo.appendChild(option);
        }
	maf_select_pf3k_col1.appendChild(maf_select_geo); 
	maf_select.appendChild(maf_select_pf3k_col1); 
	// create maf select file
	maf_select_pf3k_col2 = document.createElement("div");
	maf_select_pf3k_col2.className = "form-group col-md-2"; 
	maf_select_file_label = document.createElement("label"); 
	maf_select_file_label.className = "btn btn-default btn-file";
	var t = document.createTextNode("Choose SNP Loci File");
	maf_select_file_label.appendChild(t); 
	maf_select_file = document.createElement("input");
	maf_select_file.type = "file"; 
        maf_select_file.name = "maf_pos_select";
	maf_select_file.style = "display: none"; 
	maf_select_file_label.appendChild(maf_select_file); 
	maf_select_pf3k_col2.appendChild(maf_select_file_label);
	maf_select.appendChild(maf_select_pf3k_col2);
    }
    var maf_select_ul = document.getElementById("maf_select_ul"); 
    maf_select_ul.appendChild(maf_select);
    return;
}

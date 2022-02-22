// Add Qualtity of Cart Item
$(document).ready(function() {
    var base_url = window.location.origin;
    var path = window.location.pathname;
    var shoppingUrl = '';
    var paramStr = '';
    var count = 0

    $(".update").click(function(){
        $('input[type="number"]').each(function(index, item){
            var val = $(item).val();
            var id = $(item).attr('id');
            if(count == 0){
                paramStr += "?"+id+"="+val;
            } else {
                paramStr += "&"+id+"="+val;
            }
            count += 1;
        });

        updateUrl = base_url+"/item/update/"+paramStr;
        window.location.replace(updateUrl);
    });
});

// Get URL Parameter Values
function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

// Get URL Parameter Values (Alternative Function)
var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};

function removeUrlParam(paramSet) {
    var base_url = window.location.origin;
    var path = window.location.pathname;
    var shoppingUrl = '';
    var paramStr = '';

    var param = getUrlVars();
    count = 0;
    for (let index = 0; index < param.length; index++) {
        const element = param[index];
        var val = getUrlVars()[element];

        if (element != paramSet) {
            if (count == 0) {
                paramStr = paramStr+"?"+element+"="+val;
            }else {
                paramStr = paramStr+"&"+element+"="+val;
            }
            count = count + 1;
        }
    }

    shoppingUrl = base_url+"/shopping/"+paramStr;
    return shoppingUrl;
}

// Add Parameter to Shopping URL
function addUrlParam(paramSet, value) {
    var base_url = window.location.origin;
    var path = window.location.pathname;
    var shoppingUrl = '';
    var paramStr = '?';

    if(path != "/shopping/"){
        shoppingUrl = base_url+"/shopping/?"+paramSet+"="+value;
    }
    else {
        var param = getUrlVars();
        // Case 1 : no parameter
        if(param == base_url+"/shopping/") {
            paramStr = paramStr+paramSet+'='+value;
        } 
        // Case 2 : have parameters
        else {
            for (let index = 0; index < param.length; index++) {
                const element = param[index];
                var val = getUrlVars()[element];

                if (index == 0) {
                    paramStr = paramStr+element+"="+val;
                }else {
                    paramStr = paramStr+"&"+element+"="+val;
                }
            }

            paramStr = paramStr+"&"+paramSet+"="+value;
        }
        shoppingUrl = base_url+"/shopping/"+paramStr;
    }
    
    return shoppingUrl;
}

// Trigger for filter by Status
$(document).ready(function(){
    var base_url = window.location.origin;
    var path = window.location.pathname;

    $('#filterStatus input:radio').click(function(){
        var status_val = $('input[name=status]:checked', '#filterStatus').val();
        var shoppingUrl = '';
        var paramStr = '?';

        if(path != "/shopping/"){
            shoppingUrl = base_url+"/shopping/?status="+status_val;
        }
        else {
            var param = getUrlVars();
            // Case 1 : no parameter
            if(param == base_url+"/shopping/") {
                paramStr = paramStr+'status='+status_val;
            } 
            // Case 2 : have parameters
            else {
                paramStr = paramStr+'status='+status_val;
                for (let index = 0; index < param.length; index++) {
                    const element = param[index];
                    var val = getUrlVars()[element];
                    if(element != "status") {
                        paramStr = paramStr+"&"+element+"="+val;
                    }
                }
            }
            shoppingUrl = base_url+"/shopping/"+paramStr;
        } 
        window.location.replace(shoppingUrl);
    });
});

// Trigger for filter by District
$(document).ready(function() {
    var base_url = window.location.origin;
    var path = window.location.pathname;
    $("#filterDistrict input:radio").click(function() {
        var district_val = $('input[name=district]:checked', '#filterDistrict').val();
        var shoppingUrl = '';
        var paramStr = '?';

        if(path != "/shopping/"){
            shoppingUrl = base_url+"/shopping/?district="+district_val;
        }
        else {
            var param = getUrlVars();
            // Case 1 : no parameter
            if(param == base_url+"/shopping/") {
                paramStr = paramStr+'district='+district_val;
            } 
            // Case 2 : have parameters
            else {
                paramStr = paramStr+'district='+district_val;
                for (let index = 0; index < param.length; index++) {
                    const element = param[index];
                    var val = getUrlVars()[element];
                    if(element != "district") {
                        paramStr = paramStr+"&"+element+"="+val;
                    }
                }
            }
            shoppingUrl = base_url+"/shopping/"+paramStr;
        } 
        window.location.replace(shoppingUrl);
    });
});

// Trigger for filter by Grade
$(document).ready(function() {
    var base_url = window.location.origin;
    var path = window.location.pathname;

    $("#filterGrade input:radio").click(function() {
        var grade_val = $('input[name=grade]:checked', '#filterGrade').val();
        var shoppingUrl = '';
        var paramStr = '?';
        
        if(path != "/shopping/"){
            shoppingUrl = base_url+"/shopping/?grade="+grade_val;
        } 
        else {
            var param = getUrlVars();
            // Case 1 : no parameter
            if(param == base_url+"/shopping/") {
                paramStr = paramStr+'grade='+grade_val;
            } 
            // Case 2 : have parameters
            else {
                paramStr = paramStr+'grade='+grade_val;
                for (let index = 0; index < param.length; index++) {
                    const element = param[index];
                    var val = getUrlVars()[element];
                    if(element != "grade") {
                        paramStr = paramStr+"&"+element+"="+val;
                    }
                }
            }
            shoppingUrl = base_url+"/shopping/"+paramStr;
        }
        window.location.replace(shoppingUrl);
    });
});

// Trigger for filter by Gene
$(document).ready(function() {
    var base_url = window.location.origin;
    var shoppingUrl = '';

    $('#gene1').val(this.checked);
    $('#gene1').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene1", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene1");
            window.location.replace(shoppingUrl);
        }       
    });

    $('#gene2').val(this.checked);
    $('#gene2').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene2", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene2");
            window.location.replace(shoppingUrl);
        }          
    });

    $('#gene3').val(this.checked);
    $('#gene3').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene3", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene3");
            window.location.replace(shoppingUrl);
        }          
    });

    $('#gene4').val(this.checked);
    $('#gene4').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene4", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene4");
            window.location.replace(shoppingUrl);
        }       
    });

    $('#gene5').val(this.checked);
    $('#gene5').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene5", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene5");
            window.location.replace(shoppingUrl);
        }  
    });

    $('#gene6').val(this.checked);
    $('#gene6').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene6", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene6");
            window.location.replace(shoppingUrl);
        }          
    });

    $('#gene7').val(this.checked);
    $('#gene7').change(function() {
        if(this.checked) {
            shoppingUrl = addUrlParam("gene7", "true");
            window.location.replace(shoppingUrl);
        } else {
            shoppingUrl = removeUrlParam("gene7");
            window.location.replace(shoppingUrl);
        }          
    });

});

// Initial Checked
$(document).ready(function() {
    // District
    var district = getUrlVars()["district"];
    if (district == "all") {
        $("#district0").prop("checked", true);
    } else if (district == 1) {
        $("#district1").prop("checked", true);
    } else if (district == 2) {
        $("#district2").prop("checked", true);
    }
    else if (district == 3) {
        $("#district3").prop("checked", true);
    }

    // Status 
    var status = getUrlVars()["status"];
    if (status == "0") {
        $("#status0").prop("checked", true);
    } else if (status == 1) {
        $("#status1").prop("checked", true);
    } else if (status == 2) {
        $("#status2").prop("checked", true);
    }

    // Grade
    var grade = getUrlVars()["grade"];
    if (grade == "all") {
        $("#grade0").prop("checked", true);
    }
    else if (grade == "normal") {
        $("#grade1").prop("checked", true);
    }
    else if (grade == "premium") {
        $("#grade2").prop("checked", true);
    }

    // Gene
    var gene1 = getUrlParameter("gene1");
    if (gene1 == 'true') {
        $('#gene1').prop('checked', true);
    }

    var gene2 = getUrlParameter("gene2");
    if (gene2 == 'true') {
        $('#gene2').prop('checked', true);
    }
    
    var gene3 = getUrlParameter("gene3");
    if (gene3 == 'true') {
        $('#gene3').prop('checked', true);
    }
    
    var gene4 = getUrlParameter("gene4");
    if (gene4 == 'true') {
        $('#gene4').prop('checked', true);
    }
    
    var gene5 = getUrlParameter("gene5");
    if (gene5 == 'true') {
        $('#gene5').prop('checked', true);
    }
    
    var gene6 = getUrlParameter("gene6");
    if (gene6 == 'true') {
        $('#gene6').prop('checked', true);
    }
    var gene7 = getUrlParameter("gene7");
    if (gene7 == 'true') {
        $('#gene7').prop('checked', true);
    }
});
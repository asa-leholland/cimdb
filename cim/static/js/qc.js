console.log("I am  connected!")

  

//get component information details
function components_info(serial_number){
  console.log("clicked")
    
  valid=["P7125","P8766"]
if(true){
  var url='/product-details?'+'product_sn='+serial_number
  console.log("URL IS: ",url)
  
  window.location.href=url
}else{
  alert('only "P7125" and"P8766" are implemented for demo')

};

}

//assembel product information 
function qc_product(serial_number){
  console.log("clicked")
  alert("Product: "+serial_number+" will be QC'ed later!")
};

//report product details
function report_product(serial_number){
  console.log("clicked")
  alert("Product: "+serial_number+" will be REPORTED later!")
};


var d

fetch('/data/product_catalog')
.then(response => response.json())
.then(data => {
  console.log('Success:', data);
  d=data
})
.catch((error) => {
  console.error('Error:', error);
});

document.addEventListener('input', function (event) {

    // Only run on our select menu
	if (event.target.id !== 'product_family') return;

	// The selected value
	console.log(event.target.value);
    var family=document.getElementById("product_family").value
    console.log("selected: ",family)
    var models = document.getElementById("product_pn")
    //clear options
    models.innerHTML = ""
    console.log("Data is: ",d)
    var topmax = d[family].length
    console.log("max is: ", topmax, " and values are: ",d[family])
    // console.log("values are: ",d[family])
    for (var i = 0; i < d[family].length; i++) {
        var o = document.createElement("option");
        o.value = d[family][i]
        o.text = d[family][i]
        models.appendChild(o);
}

	// The selected option element
	console.log(event.target.options[event.target.selectedIndex]);

}, false)

// Edit product Modal
$(document).ready(function() {
  $('#pass_qc').on('shown.bs.modal', function (event) {
    	
    // Get the button that triggered the modal
		var button = $(event.relatedTarget);
    
    //Extract value from the custom data-* attribute and update modal attr
    document.getElementById("pass_qc_title").innerText=button.attr("data_product_sn")
});
});


$(document).ready(function() {
  $('#failed_qc').on('shown.bs.modal', function (event) {
    	
    // Get the button that triggered the modal
		var button = $(event.relatedTarget);
    
    //Extract value from the custom data-* attribute and update modal attr
    document.getElementById("failed_qc_title").innerText=button.attr("data_product_sn")
});
});
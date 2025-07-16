 				/* ------------ Perceval macro ------------  */


#@ String(label="Markers (sort by channel number)", style="test field") markers_names
#@ String(label="Save crops?", choices={"yes","no"}, style="radioButtonHorizontal") choice_crop
#@ String(label="Normalize all the data?", choices={"yes","no"}, style="radioButtonHorizontal") choice_normalization
#@ Integer (label = "Change normalization mean intensity value ? (default : 155)", value = 155) NormThresh
#@ String(label="Border around cells?", choices={"yes","no"}, style="radioButtonHorizontal") choice_border

// ----------- Define functions ---------------------
function atpadp_processing() {
	/*
	  Compute ATPADP ratio and process images.
	  - Calculates intensity ratio between green and red channels.
	  - Applies threshold and converts the red channel to a mask.
	  - Creates a black stack which be used lately.
	  - Performs particle analysis with smoothing, erosion, dilation, and watershed.
	  Return : Image  
	  	intermediate_image_ID : The processed time-lapse images.
	 */
	// Intensity calculator
	run("Calculator Plus", "i1=green_channel i2=red_channel operation=[Divide: i2 = (i1/i2) x k1 + k2] k1=100 k2=0 create"); 
	rename("after_calculator_plus");
	// Threshold red channel
	selectImage("red_channel");
	run("Convert to Mask", "method=Li background=Dark calculate black");
	imageCalculator("Multiply create 32-bit stack", "red_channel","after_calculator_plus");
	run("16_colors");
	run("8-bit");
	//Doesn't open images
	setBatchMode(true);
	num_of_slices = nSlices;
	close("green_channel");
	close("red_channel");
	close("after_calculator_plus");
	intermediate_image_ID = getTitle();
	// Create a black stack to fill the empty square in combine section
	newImage("test", "8-bit grayscale-mode", 100, 100, 1,0, 0);
	black_stack = getTitle();
	for (i = 0; i < num_of_slices; i++){
		selectImage(black_stack);
		run("Duplicate...", "title="+i);	
	}// Input for a list of markers sorted by channel number.
	close(black_stack);
	run("Images to Stack", "use");
	rename("black_stack");
	//------------ Analyze particles ----------------
	selectImage(intermediate_image_ID);
	run("Duplicate...", "duplicate channels=2");
	run("Smooth", "stack");
	run("Convert to Mask", "method=Li background=Dark calculate create");
	run("Erode", "stack");
	run("Dilate", "stack");
	run("Analyze Particles...", "size=10-Infinity show=Outlines display exclude clear include add slice");
	close("Results");
	// Remove small particles and empty square
	selectWindow(intermediate_image_ID+"-1");
	run("Duplicate...", "duplicate");
	run("Make Binary", "method=Huang background=Dark calculate create");
	run("Fill Holes", "stack");
	run("Watershed", "stack");
	rename("watershed_stacks");
	run("Analyze Particles...", "size=50-Infinity show=Outlines display clear include add slice");
	close("Results");
	// Preprocessing
	return intermediate_image_ID;
}
function crop_and_stack(intermediate_image){
	/*
	  Crop and stack images based on a grid system.
	 - Crop regions from the image using ROIs.
	 - Each crop is resized to 100x100 pixels and combined with adjacent crops.
	 - Add a black stack for empty areas.
	 Input : Image 
	 	The processed time-lapse images.
	 Return: Image
	 	Time-lapse cell array
	 */
	for (i=0; i<grid_size;i++){
		index_coord = i*grid_size;
		// Last iteration
		if(index_coord>=coord){
			break;
		}else{
		selectImage(intermediate_image); 
		run("Duplicate...", "duplicate");
	    roiManager("Select", index_coord);
	    run("Crop");    
		}
	    // Crop in 100x100 window
		run("Canvas Size...", "width=100 height=100 position=Center zero");
	    rename("combined"+index_coord);
	    for (j=1; j<grid_size; j++){
	    	// Last line combination
	    	if(j+index_coord>=coord){
	    		selectImage("combined" + (j + index_coord - 1));
				run("8-bit");
	    		selectImage("black_stack"); 
	    		run("8-bit");
				run("Duplicate...", "duplicate");
				rename("black_stack_combined");
				run("Combine...", "stack1=combined"+j+index_coord-1+" stack2=black_stack_combined");
				rename("combined"+j+index_coord);
	    	}else {
		    	selectImage(intermediate_image); 
				run("Duplicate...", "duplicate");
			    roiManager("Select", j+index_coord);
			    run("Crop");    
			    // Crop in 100x100 window
				run("Canvas Size...", "width=100 height=100 position=Center zero");
				rename("combined"+j+index_coord);
				run("Combine...", "stack1=combined"+j+index_coord-1+" stack2=combined"+j+index_coord);
				rename("combined"+j+index_coord);
	    	}
	    }
	    rename("line"+i);
	    run("8-bit");
	    // Combine lines
	    if(i>0){
	    	run("8-bit");
	    	run("Combine...", "stack1=line"+i-1+ " stack2=line"+i + " combine");
	    	rename("line"+i);
	    }    
	}
}
function normalization(){
	 /* 
	   Normalizes an image stack by adjusting pixel intensities based on the mean intensity of 
	   each ROI. If 'choice_normalization' is "yes":
	   - Converts the image to binary using Li's method and analyzes particles.
	   - For each ROI, calculates a normalization factor based on the target threshold
	     and applies it to the image stack.
	   - Displays the result using a 16-color LUT.
	   Requirements:
	   - 'choice_normalization': "yes" or "no" to enable normalization.
	   - 'NormThresh': The desired intensity threshold for normalization.
	   Input : Image 
	 	 Time-lapse cell array
	   Return: Image
	 	 Normalized time-lapse cell array
	  */
	if (choice_normalization == "yes"){
		run("8-bit");
		image_ID = getImageID();
		run("Duplicate...", "ignore duplicate");
		run("Make Binary", "method=Huang background=Dark calculate black create");
		run("Analyze Particles...", "size=50-Infinity show=Outlines display clear include add slice");
		close("Results");
		selectImage(image_ID); 
		coord=roiManager("size");
		for (i=0; i<coord;i++){
			roiManager("Select", i);
			selectImage(image_ID); 
			run("Measure");
			intens = getValue("Mean");
			factor = NormThresh/intens;
			run("Multiply...", "value="+factor+" stack");	
		}
	}
	run("16_colors");
}
function save_crop_add_border(to_crop_image, marker_name){
	/*
	  Save cropped images and add a border around the particles if specified.
	  - If cropping is enabled, divides the image into 100x100 pixel sections and saves non-empty crops.
	  - Crops are saved in a designated folder based on the marker name and input image.
	  - If a border is requested, adds a white grid around particles in the image.
	  - The final image, with or without a border, is saved in the output folder.
	  Inputs: Image
	  	The image to crop.
	  		  String
	  	marker_name : The marker name used for output file naming.
	 */
	if (choice_crop == "yes"){
		//Create a new folder to save crops
		indiv_crop_folder = path + "indiv_crop";
		File.makeDirectory(indiv_crop_folder);
		folder_crops = path + "indiv_crop" + File.separator + input_image_title_without_extension + "_"+ marker_name +"_outputs_indiv_crop";
		File.makeDirectory(folder_crops);
		A=100;   //Size of local area in pixels
		w = getWidth();
		h = getHeight();
		image_input = getImageID();
		for (ii=0;ii<h/A;ii++){
	        for (i=0;i<w/A;i++){
        		selectImage(image_input);
        		run("Duplicate...", "ignore duplicate");
                x=i*A;
                y=ii*A;
                makeRectangle(x, y, A, A);
                run("Crop");
				run("Measure");
				intens = getValue("Mean");
				if (intens != 0){
					title_for_crop = folder_crops + File.separator + ii + "_" + i + "_crop_" + input_image_title_without_extension + ".tif";
					saveAs("TIF", title_for_crop);	
				}	
				selectImage(to_crop_image);	
	        }
		}
	
	}
	// ---------- Add border -----------
	marker_folder = path + File.separator + marker_name + "_outputs";
	File.makeDirectory(marker_folder);
	//Create white grid around particles to delimite them
	if (choice_border == "yes") {
		width = getWidth();
		height = getHeight();
		run("Colors...", "foreground=white background=black selection=white");
		for (i = 100; i < width; i+=100) {
			makeLine(i, height, i, 0);
			run("Draw", "stack");
		}
		for (i = 100; i < height; i+=100) {
			makeLine(0, i, width, i);
			run("Draw", "stack");
		}
		run("Select All");
		title_to_save = marker_name+"_combined_border_" +input_image_title_without_extension+ ".tif";
		
		if (marker_name == "ATPADP"){
			if (choice_normalization == "yes"){
			title_to_save = marker_name + "normalized_combined_border_" +input_image_title_without_extension+ ".tif";
			}
		}
	}else{
		title_to_save = marker_name+ "_combined_" +input_image_title_without_extension+ ".tif";
	}
	output_stacks = getTitle();
	//Save images in the same directory as the original input
	selectWindow(output_stacks);
	saveAs("TIF", marker_folder + File.separator + title_to_save);
	close("Results");
	setBatchMode(false);	
}
//------------ Get files information ----------------
//Get image name and id
input_image_title = getTitle();
//Remove extension
dotIndex = indexOf(input_image_title, ".");
input_image_title_without_extension = substring(input_image_title, 0, dotIndex);
//Get file directory
path = getDirectory("image");
// Marker(s) analysis 
markers = split(markers_names, ","); 
// ----------- Obtain ATP:ADP ratio ---------------------   
run("Options...", "iterations=1 count=1");
run("Smooth"); // remove noise
// Get all the channels
run("Split Channels");
// Process image depending on markers number 
if (markers.length == 3){
	saveAs("TIF", path + File.separator + markers[2]+"_channel_" + input_image_title);
	rename("blue_channel");
	run("Put Behind [tab]");
	saveAs("TIF", path + File.separator + markers[1]+"_channel_" + input_image_title);
	rename("green_channel");
	run("Put Behind [tab]");
	saveAs("TIF", path + File.separator + markers[0]+"_channel_" + input_image_title);
	rename("red_channel");
	// ATP ADP
	intermediate_image_ID = atpadp_processing();
	coord=roiManager("size");
	// Crop and stack 
	grid_size = Math.ceil(Math.sqrt(coord));
	total_values = pow(floor(Math.sqrt(coord)),2);
	crop_and_stack(intermediate_image_ID);
	normalization();
	to_crop_image = getImageID();
	array_atpadp = markers[1]+ markers[0];
	save_crop_add_border(to_crop_image, array_atpadp);
	run("Select All");
	// MARKER +1
	open(path + File.separator + markers[0]+"_channel_" + input_image_title);
	rename("red_channel");
	open(path + File.separator + markers[2]+"_channel_" + input_image_title);
	rename("blue_channel");
	blue_channel_stack = getTitle();
	open(path + File.separator + markers[1]+"_channel_" + input_image_title);
	rename("green_channel");
	blue_channel = atpadp_processing();
	coord=roiManager("size");
	crop_and_stack(blue_channel_stack);
	run("Blue");
	to_crop_image_blue = getImageID();
	save_crop_add_border(to_crop_image_blue, markers[2]);
	close("Results");
	close("Result of red_channel");
	close("blue_channel"); 
	close("green_channel");
	close("red_channel");
	File.delete(path + File.separator + markers[0]+"_channel_" + input_image_title)
	File.delete(path + File.separator + markers[1]+"_channel_" + input_image_title)
	File.delete(path + File.separator + markers[2]+"_channel_" + input_image_title)
	setBatchMode(false);
}
if (markers.length == 4){
	saveAs("TIF", path + File.separator + markers[3]+"_channel_" + input_image_title);
	rename("gray_channel");
	run("Put Behind [tab]");
	saveAs("TIF", path + File.separator + markers[2]+"_channel_" + input_image_title);
	rename("green_channel");
	run("Put Behind [tab]");
	saveAs("TIF", path + File.separator + markers[1]+"_channel_" + input_image_title);
	rename("blue_channel");
	run("Put Behind [tab]");
	saveAs("TIF", path + File.separator + markers[0]+"_channel_" + input_image_title);
	rename("red_channel");
	// ATP ADP
	intermediate_image_ID = atpadp_processing();
	coord=roiManager("size");
	// Crop and stack 
	grid_size = Math.ceil(Math.sqrt(coord));
	total_values = pow(floor(Math.sqrt(coord)),2);
	crop_and_stack(intermediate_image_ID);
	normalization();
	to_crop_image = getImageID();
	array_atpadp = markers[2]+ markers[0];
	save_crop_add_border(to_crop_image, array_atpadp);
	run("Select All");	
	// MARKER +1
	open(path + File.separator + markers[0]+"_channel_" + input_image_title);
	rename("red_channel");
	open(path + File.separator + markers[1]+"_channel_" + input_image_title);
	rename("blue_channel");
	blue_channel_stack = getTitle();
	open(path + File.separator + markers[2]+"_channel_" + input_image_title);
	rename("green_channel");
	open(path + File.separator + markers[3]+"_channel_" + input_image_title);
	rename("gray_channel");
	blue_channel = atpadp_processing();
	coord=roiManager("size");
	crop_and_stack(blue_channel_stack);
	run("Blue");
	to_crop_image_blue = getImageID();
	save_crop_add_border(to_crop_image_blue, markers[1]);
	close("Results");
	close("Result of red_channel");
	close("gray_channel"); 
	close("blue_channel"); 
	close("green_channel");
	close("red_channel");
	setBatchMode(false);
	// MARKER +2
	open(path + File.separator + markers[0]+"_channel_" + input_image_title);
	rename("red_channel");
	open(path + File.separator + markers[1]+"_channel_" + input_image_title);
	rename("blue_channel");
	open(path + File.separator + markers[2]+"_channel_" + input_image_title);
	rename("green_channel");
	open(path + File.separator + markers[3]+"_channel_" + input_image_title);
	rename("gray_channel");
	gray_channel_stack = getTitle();
	gray_channel = atpadp_processing();
	coord=roiManager("size");
	crop_and_stack(gray_channel_stack);
	run("Grays");
	to_crop_image_gray = getImageID();
	save_crop_add_border(to_crop_image_gray, markers[3]);
	//add_border_marker(markers[3]);
	close("Results");
	close("Result of red_channel");
	close("gray_channel"); 
	close("blue_channel"); 
	close("green_channel");
	close("red_channel");
	File.delete(path + File.separator + markers[0]+"_channel_" + input_image_title)
	File.delete(path + File.separator + markers[1]+"_channel_" + input_image_title)
	File.delete(path + File.separator + markers[2]+"_channel_" + input_image_title)
	File.delete(path + File.separator + markers[3]+"_channel_" + input_image_title)
	setBatchMode(false);
	
}
if (markers.length == 2) {
	close();
	saveAs("TIF", path + File.separator + markers[1]+"_channel_" + input_image_title);
	rename("green_channel");
	run("Put Behind [tab]");
	saveAs("TIF", path + File.separator + markers[0]+"_channel_" + input_image_title);
	rename("red_channel");
	// ATP ADP
	intermediate_image_ID = atpadp_processing();
	coord=roiManager("size");
	// Crop and stack 
	grid_size = Math.ceil(Math.sqrt(coord));
	total_values = pow(floor(Math.sqrt(coord)),2);
	crop_and_stack(intermediate_image_ID);
	normalization();
	to_crop_image = getImageID();
	array_atpadp = markers[1]+ markers[0];
	save_crop_add_border(to_crop_image, array_atpadp);
	run("Select All");
	File.delete(path + File.separator + markers[0]+"_channel_" + input_image_title)
	File.delete(path + File.separator + markers[1]+"_channel_" + input_image_title)
}

close("Log");

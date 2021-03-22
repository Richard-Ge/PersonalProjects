//-----------------------------------------------------------------------------
// 
// Formats my time-log-sample data into a .csv for analysis (using R, NumPy, etc.)
//
//-----------------------------------------------------------------------------

#include<stdio.h>
#include<stdlib.h>
#include<ctype.h>
#include<assert.h>
#include<string.h>

#define MAX_STRING_LENGTH 100

// function prototype 
void extract_entry(char* s, char* a);

void copy_date(char* s, char* result);

// function main which takes command line arguments 
int main(int argc, char* argv[]){
	printf("=========start========\n");  // DEBUG
	FILE* in;		  // handle for input file						
	FILE* out;		 // handle for output file					  
	char* line;		// string holding input line				  
	char* formatted_entry; // string holding all alpha-numeric chars 

	// check command line for correct number of arguments 
	if( argc != 3 ){
		printf("Usage: %s input-file output-file\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	// open input file for reading 
	if( (in=fopen(argv[1], "r"))==NULL ){
		printf("Unable to read from file %s\n", argv[1]);
		exit(EXIT_FAILURE);
	}

	// open output file for writing 
	if( (out=fopen(argv[2], "w"))==NULL ){
		printf("Unable to write to file %s\n", argv[2]);
		exit(EXIT_FAILURE);
	}
	fprintf(out, "Date,Starttime,Endtime,Activity,Det1,Det2\n");

	// allocate strings line and formatted_entry on the heap 
	char* line_i = calloc(MAX_STRING_LENGTH+1, sizeof(char) );
	formatted_entry = calloc(MAX_STRING_LENGTH+1, sizeof(char) );
	assert( line_i!=NULL && formatted_entry!=NULL );

	// read each line in input file, extract alpha-numeric characters 
	char* this_date = calloc(11, sizeof(char));
	while( fgets(line_i, MAX_STRING_LENGTH, in) != NULL ){
		// fprintf(out, "==New Line: %s\n", line_i);  //DEBUG
		// if it's a date
		if(line_i[1]=='/' || line_i[2]=='/') {
		// save the date 						// free(this_date);  // frees the old date...unneeded?  // this_date = calloc(11, sizeof(char));
			copy_date(line_i, this_date);  // problem: line_i gets unintentionally reassigned at the next entry. solution: method to write to this char array
			// fprintf(out, "This date: %s\n", this_date);  //DEBUG
		} else {  // if(line_i[1]!='/' && line_i[2]!='/') DeMorgan's!
		// if not, it's an entry (or "==")
		// format an entry
			extract_entry(line_i, formatted_entry);
			int last_char = strlen(formatted_entry)-1;
			if(formatted_entry[last_char]==',') {  // when the input line ends with space, the output will have a ',' at the end
				formatted_entry[last_char] = '\0';
			} 
			// save it to output file (if it's not "==")

			// fprintf(out, "Extracted: %s\n", formatted_entry);  //DEBUG
			// fprintf(out, "This date 2: %s\n", this_date);  //DEBUG
			if(formatted_entry[last_char-1] != '=')
				fprintf(out, "%s%s%s\n", this_date, ",", formatted_entry);
		}
	}

	// free heap memory 
	free(line_i);
	free(formatted_entry);
	free(this_date);

	// close input and output files 
	fclose(in);
	fclose(out);

	return EXIT_SUCCESS;
}

//needed to copy pointer contents, before theyre reassigned
void copy_date(char* s, char* result) {  
	int i;
	for(i = 0; s[i]!='\n' && s[i]!=' '; i++) {
		result[i] = s[i];
	}
	result[i] = '\0';
}

// function definitions
void extract_entry(char* input_line, char* csv_line) {
	int numWords = 0;  // number of words on a line
	int i = 0;
	int j = 0;  // for formatting ": ", i will be slightly ahead of j
	for(i = 0; numWords<5 && input_line[i]!='\n'; i++) {
		if(input_line[i]=='(') {
			break;  // numWords+=4; ends the line 1 char too late
		} else if(input_line[i]=='-' || input_line[i]==' ') {
			// needs separation normally if "-" or " "
			csv_line[j] = ',';
			numWords++;
		} else if((input_line[i]==':' || input_line[i]==',') && input_line[i+1]==' ') {
			// needs bigger separation if "; " or ", "
			csv_line[j] = ','; 
			i++; 
			numWords++; 
		} else {
			// just a letter/number
			csv_line[j] = input_line[i];
		}
		j++;
	}
	// add more commas so .csv is made correctly. there will be 6 on each line (incl. times)
	for(int commaI = numWords; commaI<5 && csv_line[j-1]!='='; commaI++) {
		csv_line[j] = ',';
		j++;
	}
	csv_line[j] = '\0';  // need to stop the string 
}



/****************************************************************************
 * Configuration.cpp Implementation File
 *
 * Created by Erman Gurses on 2/8/16.
 * Modified by Rutuja Patil on 3/8/2016.
 * Modified by Sarah Willer in June 2016: 
 *     > hasConflict() added to prevent dup name or val by addParams
 *     > calls to hasConflict() added to addParam methods
****************************************************************************/
#include <cstring>
#include <stdexcept>
#include <iostream>
#include <map>
#include <sstream>
#include <stdlib.h>
#include <string>

#include "Configuration.h"

/****************************************************************************
 *
 * parseInt() helper function
 *
****************************************************************************/
int Configuration::parseInt(char* str){
    return (int) strtol( str, NULL, 10 );
}

/****************************************************************************
 *
 * Constructor that parses command line.
 *
****************************************************************************/
Configuration::Configuration() : mCount(0) {
    mUsageString = "usage: %s\n";
    // initialize help and verify as default params for all benchmarks
	addParamBool("help",'h', false, "--help, usage help for this dialogue\n");
	addParamBool("v", 'v', false, "-v, verify output\n");
}

/****************************************************************************
 *
 * Destructor
 *
****************************************************************************/
Configuration::~Configuration(){
// for (int  i = 0; i < mCount; i++){
//     std::cerr << "delete: " << std::strlen(mLongOptions[i].name) + 1 << " bytes.\n";
//     delete mLongOptions[i].name;
// }
} 
/****************************************************************************
 *
 * Method to parse() commandLine
 *
****************************************************************************/
void Configuration::parse(int argc,char* argv[]){
    int c;
    mExecName = std::string(argv[0]);     //executable is always here
    do {
        int option_index = 0;
        // lookup index of command char in mLongOptions array
        c = getopt_long(argc, argv, mCommandChars.c_str(), mLongOptions,
                        &option_index);
         //If this is a known character then process it.
        if (mKnownChars.find(c)!=mKnownChars.end()) {
            processArgVal(mCharToFieldname[c], optarg);
        }
         if (c == 'h') {
            std::cout << mUsageString << "\n";
            exit(0);
        }
    } while (c!=-1);
}

/****************************************************************************
 *
 * toLDAPString() Method
 *
****************************************************************************/
std::string Configuration::toLDAPString()
{ 
    std::stringstream ldap;
    ldap << "Executable:" << mExecName << ",";
    bool first = true;
    for (std::list<int>::iterator iter=mCharOrder.begin();
            iter!=mCharOrder.end(); iter++) {
        if (!first) { ldap << ","; }
        else { first = false; }
        ldap << mCharToFieldname[*iter] << ":" 
           << mIntMap[mCharToFieldname[*iter]];

    }
    ldap << ",";
    return  ldap.str();
}

/****************************************************************************
 *
 * Returns bool type false if fieldname or command character are unique
 *
****************************************************************************/

bool Configuration::hasConflict(std::string fieldname, char commandChar){

    for (int  i = 0; i < mCount; i++){
        if ((mLongOptions[i].name == fieldname) || (mLongOptions[i].val == 
                commandChar)) {
            std::cout << "Invalid Arg=" << mLongOptions[i].name << ":" << mLongOptions[i].val << " " << std::endl;
            throw std::invalid_argument("Invalid argument: Fieldname or command char already in use");
        }
    }
    return false;
}     

/****************************************************************************
 *
 * Methods that add fields to configuration.
 *
****************************************************************************/
void Configuration::addParamInt(std::string fieldname, char single_char, 
                                int init_val, std::string help_str) {
    //std::cerr << "addParamInt('" << fieldname << "','" << single_char << "'," << init_val << ",'" << help_str << "'\n";
    // check for duplicate
    /* Commenting out hasConflict for now as giving inexplicable errors... */
    //hasConflict(fieldname, single_char);
    mIntMap[fieldname] = init_val;
    
    mCharToFieldname[single_char] = fieldname;
    mKnownChars.insert(single_char);
    mCharOrder.push_back(single_char);
    
    mUsageString += help_str + "\n";
    
    mCommandChars += std::string(1,single_char) + ":";

    // Set up the long options data structure.
    // Assuming all arguments are optional for now.
    //char* temp = new char[fieldname.length()+1];
    //std::cerr << "new: " << fieldname.length()+1 << " bytes.\n";
    //std::strcpy (temp, fieldname.c_str());
    mLongOptions[mCount].name = fieldname.c_str(); //temp;
    // required_argument indicates need for int value after flag
    mLongOptions[mCount].has_arg = required_argument;
    mLongOptions[mCount].flag = 0;
    mLongOptions[mCount].val = single_char;
    mCount++;

    terminateOptionsArray();
}

/****************************************************************************
 *
 * Methods that add fields to configuration.
 *
****************************************************************************/
void Configuration::addParamBool(std::string fieldname, char single_char,
        bool init_val, std::string help_str) {
    // check for duplicate
    //hasConflict(fieldname, single_char);
    mBoolMap[fieldname] = init_val;
    mCharToFieldname[single_char] = fieldname;
    mKnownChars.insert(single_char);
    mUsageString += help_str + "\n";
    mCommandChars += std::string(1,single_char);
 
    // Set up the long options data structure.
    // Assuming all arguments are optional for now.
    //char* temp = new char[fieldname.length()+1];
    //std::cerr << "new: " << fieldname.length()+1 << " bytes.\n";
    //std::strcpy (temp, fieldname.c_str());
    mLongOptions[mCount].name = fieldname.c_str(); //temp;
    // required_argument indicates need for int value after flag
    mLongOptions[mCount].has_arg = no_argument;
    mLongOptions[mCount].flag = 0;
    mLongOptions[mCount].val = single_char;
    mCount++;

    terminateOptionsArray();
}

/****************************************************************************
 *
 * Method that add fields to configuration
 *
****************************************************************************/
void Configuration::addParamString(std::string fieldname,char single_char,
      std::string init_val,std::string help_str){
    // check for duplicate
    //hasConflict(fieldname, single_char);
    mStringMap[fieldname] = init_val;
    mCharToFieldname[single_char] = fieldname;
      
    mKnownChars.insert(single_char);
    mCharOrder.push_back(single_char);

    mUsageString += help_str + "\n";

    mCommandChars += std::string(1,single_char) + ":";

    // Set up the long options data structure.
    // Assuming all arguments are optional for now.
    //char* temp = new char[fieldname.length()+1];
    //std::cerr << "new: " << fieldname.length()+1 << " bytes.\n";
    //std::strcpy (temp, fieldname.c_str());
    mLongOptions[mCount].name = fieldname.c_str(); //temp;
    // required_argument indicates need for string value after flag
    mLongOptions[mCount].has_arg = required_argument;
    mLongOptions[mCount].flag = 0;
    mLongOptions[mCount].val = single_char;
    mCount++;
    
    terminateOptionsArray();
}  

/****************************************************************************
 *
 * terminate mLongOptions[]
 *
****************************************************************************/
void Configuration::terminateOptionsArray() {
    mLongOptions[mCount].name = 0;
    mLongOptions[mCount].has_arg = 0;
    mLongOptions[mCount].flag = 0;
    mLongOptions[mCount].val = 0;
}

/****************************************************************************
 *
 * Method that processes parsed field values.
 *
****************************************************************************/
void Configuration::processArgVal(std::string fieldname, char* arg_val) {

    // use the fieldname to locate which map we are looking in
    if (mIntMap.find(fieldname)!=mIntMap.end()) {
        mIntMap[fieldname] = parseInt( arg_val );
    } else if(mBoolMap.find(fieldname) != mBoolMap.end()){
    	mBoolMap[fieldname] = 1;
    } else if(mStringMap.find(fieldname) != mStringMap.end()) {
        mStringMap[fieldname] = std::string(arg_val);
    } else {
        std::cerr << "Unknown fieldname: " << fieldname << std::endl;
        exit(-1);
    }
}
/****************************************************************************
 *
 * Method that returns int type fieldValue given fieldname.
 *
****************************************************************************/

int Configuration::getInt(std::string fieldname){

    if (mIntMap.find(fieldname) != mIntMap.end()){
        return mIntMap[fieldname];
    } else {
        std::cerr << "Unknown fieldname: " << fieldname << std::endl;
        exit(-1);
    }
}

/****************************************************************************
 *
 * Method that returns bool type fieldValue given fieldname.
 *
****************************************************************************/

bool Configuration::getBool(std::string fieldname){

    if (mBoolMap.find(fieldname) != mBoolMap.end()){
        return mBoolMap[fieldname];
    } else {
        std::cerr << "Unknown fieldname: " << fieldname << std::endl;
        exit(-1);
    }
}


/****************************************************************************
 *
 * Method that returns String type filedValue given fieldname.
 *
****************************************************************************/

std::string Configuration::getString(std::string fieldname){

   if(mStringMap.find(fieldname) != mStringMap.end()){
      return mStringMap[fieldname];
   }else{
     std::cerr << "Unknown fieldname: " << fieldname << std::endl;
     exit(-1);

   }

} 



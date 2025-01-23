#include <vector>
#include <map>
#include <iostream>
#include <string>
#include <sstream>

#include <fstream>
#include <stdio.h>
#ifdef _WIN32
  #include <Windows.h>  // to define Sleep()
#else
  #include <unistd.h>   // POSIX sleep()
#endif


#include <octomap/ColorOcTree.h>
#include <octomap/octomap.h>
#include <octomap/OcTreeStamped.h>
#include <octomap/math/Utils.h>

using namespace std;
using namespace octomap;
using namespace octomath;

class Command_Line_Argument_Parser {
protected:
	std::string command;
	std::string usage;

	std::vector<std::string> lone_arguments;
	std::map<std::string, std::string> flag_arguments;
public:
	Command_Line_Argument_Parser(int argc, char *argv[]) ;

	std::vector<std::string> get_lone_arguments();
	std::map<std::string, std::string> get_flag_arguments();

	std::string get_command();
};

Command_Line_Argument_Parser::Command_Line_Argument_Parser(int argc, char *argv[]) {
	int next_arg_index = 0;
	char *arg = NULL;

	command = argv[0];
	for (
		int arg_index = 1;
		arg_index < argc;
		arg_index++
	) {
		next_arg_index = arg_index + 1;

		if ( argv[arg_index][0] == '-') {

			if ( argv[arg_index][1] == '\0' ) {
				flag_arguments.insert( std::pair<std::string, std::string>(
					argv[arg_index],
					std::string()
				) );
			} else if ( next_arg_index < argc ) {
				arg = argv[next_arg_index];
				flag_arguments.insert( std::pair<std::string, std::string>(
					argv[arg_index],
					argv[next_arg_index]
				) );
				arg_index++;
			}
		} else {
			lone_arguments.push_back(argv[arg_index]);
		}
	}
}

std::string Command_Line_Argument_Parser::get_command() { return command; }
std::vector<std::string> Command_Line_Argument_Parser::get_lone_arguments() { return lone_arguments; }
std::map<std::string, std::string> Command_Line_Argument_Parser::get_flag_arguments() { return flag_arguments; }

int main(int argc, char *argv[]) {

	Command_Line_Argument_Parser parser{argc,argv};
	std::map<std::string,std::string> flag_args = parser.get_flag_arguments();

	if (
		flag_args["--xyz_csv"].empty() ||
		flag_args["--out"].empty()
	) {
		std::cout << parser.get_command()
			<< " --xyz_csv <xyz csv point cloud file> --out <output octomap file>\n";
		return -1;
	}

	Pointcloud point_cloud;
	OcTreeStamped tree(10);
	std::ifstream infile(flag_args["--xyz_csv"]);
	if ( !infile ) {
		std::cout << "could not open file\n";
		return -1;
	}

	std::string line;
	std::getline(infile,line);

	while ( std::getline(infile,line) ) {

		std::stringstream ss(line);
		// std::cout << "ss.str(): " << ss.str() << "\n";
		if ( !ss.good() ) {
			std::cout << "Could not get x\n";
			return -2;
		}

		std::string substr;
		std::getline(ss, substr, ',');
		// std::cout << "ss.str(): " << ss.str() << "\n";
		// std::cout << "substr: " << substr << "\n";
		float x = std::stof(substr);
		if ( !ss.good() ) {
			std::cout << "Could not get y\n";
			return -3;
		}

		std::getline(ss, substr, ',');
		// std::cout << "ss.str(): " << ss.str() << "\n";
		// std::cout << "substr: " << substr << "\n";
		float y = std::stof(substr);
		if ( !ss.good() ) {
			std::cout << "Could not get z\n";
			return -4;
		}

		std::getline(ss, substr, '\n');
		// std::cout << "ss.str(): " << ss.str() << "\n";
		// std::cout << "substr: " << substr << "\n";
		float z = std::stof(substr);
		// if ( !ss.good() ) {
		// 	std::cout << "Could not get z\n";
		// 	return -5;
		// }

		// std::cout << "(x,y,z): " << "(" << x << "," << y << "," << z << ")\n";
		// point3d begin(0.0,0.0,0.0);
		point3d end(x,y,z);
		tree.updateNode(end,true);
		// point_cloud.push_back(end);
		// tree.insertRay(begin,end);
	}

	point3d begin(0.0,0.0,0.0);
	// tree.insertPointCloudRays(point_cloud,begin);
	// tree.insertPointCloud(point_cloud,begin);
	tree.toMaxLikelihood();
	tree.updateInnerOccupancy();

	// std::cout << "tree.writeBinary(\"" << flag_args["--out"] << "\");\n";
	tree.writeBinary(flag_args["--out"]);
	std::cout << "\n";
}

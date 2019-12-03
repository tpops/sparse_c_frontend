#ifndef INTSETLIB_HPP
#define INTSETLIB_HPP

#include <string>
#include <isl/ast.h>
#include <isl/ast_build.h>
#include <isl/options.h>
#include <isl/space.h>
#include <isl/set.h>
#include <isl/union_set.h>
#include <isl/union_map.h>
#include <isl/stream.h>
#include <isl/schedule_node.h>
using std::string;

namespace {
    struct IntSetLib {
    private:
        struct options {
            struct isl_options	*isl;
            unsigned		 atomic;
            unsigned		 separate;
        };

        ISL_ARGS_START(struct options, options_args)
                        ISL_ARG_CHILD(struct options, isl, "isl", &isl_options_args, "isl options")
                        ISL_ARG_BOOL(struct options, atomic, 0, "atomic", 0,
                                     "globally set the atomic option")
                        ISL_ARG_BOOL(struct options, separate, 0, "separate", 0,
                                     "globally set the separate option")
        ISL_ARGS_END

        ISL_ARG_DEF(cg_options, struct options, options_args)
        ISL_ARG_CTX_DEF(cg_options, struct options, options_args)

/* Return a universal, 1-dimensional set with the given name.
 */
        static __isl_give isl_union_set *universe(isl_ctx *ctx, const char *name)
        {
            isl_space *space;

            space = isl_space_set_alloc(ctx, 0, 1);
            space = isl_space_set_tuple_name(space, isl_dim_set, name);
            return isl_union_set_from_set(isl_set_universe(space));
        }

/* Set the "name" option for the entire schedule domain.
 */
        static __isl_give isl_union_map *set_universe(__isl_take isl_union_map *opt,
                                                      __isl_keep isl_union_map *schedule, const char *name)
        {
            isl_ctx *ctx;
            isl_union_set *domain, *target;
            isl_union_map *option;

            ctx = isl_union_map_get_ctx(opt);

            domain = isl_union_map_range(isl_union_map_copy(schedule));
            domain = isl_union_set_universe(domain);
            target = universe(ctx, name);
            option = isl_union_map_from_domain_and_range(domain, target);
            opt = isl_union_map_union(opt, option);

            return opt;
        }

/* Update the build options based on the user-specified options.
 *
 * If the --separate or --atomic options were specified, then
 * we clear any separate or atomic options that may already exist in "opt".
 */
        static __isl_give isl_ast_build *set_options(__isl_take isl_ast_build *build,
                                                     __isl_take isl_union_map *opt, struct options *options,
                                                     __isl_keep isl_union_map *schedule)
        {
            if (options->separate || options->atomic) {
                isl_ctx *ctx;
                isl_union_set *target;

                ctx = isl_union_map_get_ctx(schedule);

                target = universe(ctx, "separate");
                opt = isl_union_map_subtract_range(opt, target);
                target = universe(ctx, "atomic");
                opt = isl_union_map_subtract_range(opt, target);
            }

            if (options->separate)
                opt = set_universe(opt, schedule, "separate");
            if (options->atomic)
                opt = set_universe(opt, schedule, "atomic");

            build = isl_ast_build_set_options(build, opt);

            return build;
        }

/* Construct an AST in case the schedule is specified by a union map.
 *
 * We read the context and the options from "s" and construct the AST.
 */
        static __isl_give isl_ast_node *construct_ast_from_union_map(
                __isl_take isl_union_map *schedule, __isl_keep isl_stream *s)
        {
            isl_set *context;
            isl_union_map *options_map;
            isl_ast_build *build;
            isl_ast_node *tree;
            struct options *options;

            options = isl_ctx_peek_cg_options(isl_stream_get_ctx(s));

            context = isl_stream_read_set(s);
            options_map = isl_stream_read_union_map(s);

            build = isl_ast_build_from_context(context);
            build = set_options(build, options_map, options, schedule);
            tree = isl_ast_build_node_from_schedule_map(build, schedule);
            isl_ast_build_free(build);

            return tree;
        }

/* If "node" is a band node, then replace the AST build options
 * by "options".
 */
        static __isl_give isl_schedule_node *node_set_options(
                __isl_take isl_schedule_node *node, void *user)
        {
            enum isl_ast_loop_type *type = (isl_ast_loop_type *) user;
            int i, n;

            if (isl_schedule_node_get_type(node) != isl_schedule_node_band)
                return node;

            n = isl_schedule_node_band_n_member(node);
            for (i = 0; i < n; ++i)
                node = isl_schedule_node_band_member_set_ast_loop_type(node,
                                                                       i, *type);
            return node;
        }

/* Replace the AST build options on all band nodes if requested
 * by the user.
 */
        static __isl_give isl_schedule *schedule_set_options(
                __isl_take isl_schedule *schedule, struct options *options)
        {
            enum isl_ast_loop_type type;

            if (!options->separate && !options->atomic)
                return schedule;

            type = options->separate ? isl_ast_loop_separate : isl_ast_loop_atomic;
            schedule = isl_schedule_map_schedule_node_bottom_up(schedule,
                                                                &node_set_options, &type);

            return schedule;
        }

/* Construct an AST in case the schedule is specified by a schedule tree.
 */
        static __isl_give isl_ast_node *construct_ast_from_schedule(
                __isl_take isl_schedule *schedule)
        {
            isl_ast_build *build;
            isl_ast_node *tree;
            struct options *options;

            options = isl_ctx_peek_cg_options(isl_schedule_get_ctx(schedule));

            build = isl_ast_build_alloc(isl_schedule_get_ctx(schedule));
            schedule = schedule_set_options(schedule, options);
            tree = isl_ast_build_node_from_schedule(build, schedule);
            isl_ast_build_free(build);

            return tree;
        }

    public:
        string codegen(const string& relation, const string& id = "I") {
            isl_ctx *ctx;
            isl_stream *s;
            isl_ast_node *tree = NULL;
            struct options *options;
            isl_printer *p;
            struct isl_obj obj;
            int stat = EXIT_SUCCESS;

            pid_t pid;
            int pipes[2];

            FILE* input = stdin;
            FILE* output = stdout;

            if (pipe(pipes)) {
                fprintf(stderr, "ERROR: cannot create pipe.\n");
                stat = EXIT_FAILURE;
            } else {
                if (pid == (pid_t) 0) {
                    pid = fork();
                    input = fdopen(pipes[1], "w");
                    output = fdopen(pipes[0], "r");

                } else {
                    fprintf (stderr, "ERROR: cannot create thread.\n");
                    stat = EXIT_FAILURE;
                }
            }

            if (stat == EXIT_SUCCESS) {
                string relId, relStr;
                size_t pos = relation.find(ASN_OP);
                if (pos != string::npos) {
                    relId = Strings::rtrim(relation.substr(0, pos - 1));
                    relStr = Strings::ltrim(relation.substr(pos + 2));
                } else {
                    relId = id;
                    relStr = relation;
                }
                fprintf(input, (relId + " := " + relStr + ";\n").c_str());
                fprintf(input, ("codegen(" + relId + ");\n").c_str());

                options = cg_options_new_with_defaults();
                //assert(options);
                ctx = isl_ctx_alloc_with_options(&options_args, options);
                isl_options_set_ast_build_detect_min_max(ctx, 1);
                //argc = cg_options_parse(options, argc, argv, ISL_ARG_ALL);

                s = isl_stream_new_file(ctx, input);
                obj = isl_stream_read_obj(s);
                if (obj.v == NULL) {
                    stat = EXIT_FAILURE;
                } else if (obj.type == isl_obj_map) {
                    isl_union_map *umap;

                    umap = isl_union_map_from_map((isl_map *) obj.v);
                    tree = construct_ast_from_union_map(umap, s);
                } else if (obj.type == isl_obj_union_map) {
                    tree = construct_ast_from_union_map((isl_union_map *) obj.v, s);
                } else if (obj.type == isl_obj_schedule) {
                    tree = construct_ast_from_schedule((isl_schedule *) obj.v);
                } else {
                    obj.type->free(obj.v);
                    isl_die(ctx, isl_error_invalid, "unknown input",
                            stat = EXIT_FAILURE);
                }
                isl_stream_free(s);

                p = isl_printer_to_file(ctx, output);
                p = isl_printer_set_output_format(p, ISL_FORMAT_C);
                p = isl_printer_print_ast_node(p, tree);

                isl_printer_free(p);
                isl_ast_node_free(tree);
                isl_ctx_free(ctx);
            }

            return "";
        }
    };
}

#endif  //INTSETLIB_HPP

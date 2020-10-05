#!/usr/bin/env node
"use strict";
exports.__esModule = true;
var requests = require("requests");
var sys = require("sys");
var re = require("re");
//import * as webbrowser from 'webbrowser';
var open = require('open');
var json = require("json");
var argparse = require("argparse");
var pprint = require("pprint");
var pathlib_1 = require("pathlib");
//import * as os from 'os';
require('dotenv').config();
require('docstring');
var os = require('os');
var opn = require('opn');
require("./string.extensions");
// String.format doesn't work
// Need to find package? Need to rewrite?
// import { String, StringBuilder } from 'typescript-string-operations';
var _pj;
var FALLBACK_CONFIG_FILE, ZENODO_API_URL, args, params, parser, parser_concept, parser_copy, parser_create, parser_download, parser_duplicate, parser_get, parser_list, parser_newversion, parser_update, parser_upload, subparsers;
function _pj_snippets(container) {
    function in_es6(left, right) {
        if (((right instanceof Array) || ((typeof right) === "string"))) {
            return (right.indexOf(left) > (-1));
        }
        else {
            if (((right instanceof Map) || (right instanceof Set) || (right instanceof WeakMap) || (right instanceof WeakSet))) {
                return right.has(left);
            }
            else {
                return (left in right);
            }
        }
    }
    container["in_es6"] = in_es6;
    return container;
}
_pj = {};
_pj_snippets(_pj);
params = {};
ZENODO_API_URL = "";
FALLBACK_CONFIG_FILE = (process.env.HOME + "/.config/zenodo-cli/config.json");
params = {};
ZENODO_API_URL = "";
/*
String.format = function() {
  var s = arguments[0];
  for (var i = 0; i < arguments.length - 1; i++) {
    var reg = new RegExp("\\{\\}", "gm");
    s = s.replace(reg, arguments[i + 1]);
  }
  return s;
}*/
function loadConfig(configFile) {
    var config;
    if (new pathlib_1.Path(configFile).is_file()) {
        configFile = configFile;
    }
    else {
        if (new pathlib_1.Path(FALLBACK_CONFIG_FILE).is_file()) {
            configFile = FALLBACK_CONFIG_FILE;
        }
        else {
            console.log("Config file not present at {} or {}".format("config.json", FALLBACK_CONFIG_FILE));
            sys.exit(1);
        }
    }
    config = json.load(open(configFile));
    params = { "access_token": config.get("accessToken") };
    if ((config.get("env") === "sandbox")) {
        ZENODO_API_URL = "https://sandbox.zenodo.org/api/deposit/depositions";
    }
    else {
        ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions";
    }
}
function parseId(id) {
    var dot_split, slash_split;
    if (id.toString().isnumeric()) {
        return id;
    }
    slash_split = id.toString().split("/").slice((-1))[0];
    if (slash_split.isnumeric()) {
        id = slash_split;
    }
    else {
        dot_split = id.toString().split(".").slice((-1))[0];
        if (dot_split.isnumeric()) {
            id = dot_split;
        }
    }
    return id;
}
function publishDeposition(id) {
    var res;
    id = parseId(id);
    res = requests.post("{}/{}/actions/publish".format(ZENODO_API_URL, id), { "params": params });
    if ((res.status_code !== 202)) {
        console.log("Error in publshing deposition {}: {}".format(id, json.loads(res.content)));
    }
    else {
        console.log("\tDeposition {} successfully published.".format(id));
    }
}
function getData(id) {
    var listParams, myres, res;
    id = parseId(id);
    res = requests.get("{}/{}".format(ZENODO_API_URL, id), { "params": params });
    if ((res.status_code !== 200)) {
        myres = json.loads(res.content);
        if ((myres["status"] !== 404)) {
            console.log("Error in getting data: {}".format(json.loads(res.content)));
            sys.exit(1);
        }
        else {
            console.log("Checking concept ID.");
            listParams = params;
            listParams["q"] = ("conceptrecid:" + id);
            res = requests.get(ZENODO_API_URL, { "params": listParams });
            if ((res.status_code !== 200)) {
                console.log("Failed in getting data: {}".format(json.loads(res.content)));
            }
            else {
                console.log(("Found record ID: " + res.json()[0]["id"].toString()));
                return res.json()[0];
            }
        }
    }
    else {
        return res.json();
    }
}
function showDepositionJSON(info) {
    console.log("Title: {}".format(info["title"]));
    if (_pj.in_es6("publication_date", info["metadata"])) {
        console.log("Date: {}".format(info["metadata"]["publication_date"]));
    }
    else {
        console.log("Date: N/A");
    }
    console.log("RecordId: {}".format(info["id"]));
    if (_pj.in_es6("conceptrecid", info.keys())) {
        console.log("ConceptId: {}".format(info["conceptrecid"]));
    }
    else {
        console.log("ConceptId: N/A");
    }
    console.log("DOI: {}".format(info["metadata"]["prereserve_doi"]["doi"]));
    console.log("Published: {}".format((info["submitted"] ? "yes" : "no")));
    console.log("State: {}".format(info["state"]));
    console.log("URL: https://zenodo.org/{}/{}".format((info["submitted"] ? "record" : "deposit"), info["id"]));
    if (_pj.in_es6("bucket", info["links"].keys())) {
        console.log("BucketURL: {}".format(info["links"]["bucket"]));
    }
    else {
        console.log("BucketURL: N/A");
    }
    console.log("\n");
}
function showDeposition(id) {
    var info;
    id = parseId(id);
    info = getData(id);
    showDepositionJSON(info);
}
function dumpJSON(info) {
    var pp;
    pp = new pprint.PrettyPrinter({ "indent": 4 });
    pp.pprint(info);
    console.log("\n");
}
function dumpDeposition(id) {
    var info;
    id = parseId(id);
    info = getData(id);
    dumpJSON(info);
}
function getMetadata(id) {
    return getData(id)["metadata"];
}
function parseIds(genericIds) {
    return function () {
        var _pj_a = [], _pj_b = genericIds;
        for (var _pj_c = 0, _pj_d = _pj_b.length; (_pj_c < _pj_d); _pj_c += 1) {
            var id = _pj_b[_pj_c];
            _pj_a.push(parseId(id));
        }
        return _pj_a;
    }
        .call(this);
}
function saveIdsToJson(args) {
    var data, f, ids;
    ids = parseIds(args.id);
    for (var id, _pj_c = 0, _pj_a = ids, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
        id = _pj_a[_pj_c];
        f = open("{}.json".format(id), "w");
        data = getData(id);
        json.dump(data["metadata"], f);
        f.close();
        finalActions(args, id, data["links"]["html"]);
    }
}
function createRecord(metadata) {
    var res, response_data;
    console.log("\tCreating record.");
    res = requests.post(ZENODO_API_URL, { "json": { "metadata": metadata }, "params": params });
    if ((res.status_code !== 201)) {
        console.log("Error in creating new record: {}".format(json.loads(res.content)));
        sys.exit(1);
    }
    response_data = res.json();
    return response_data;
}
function editDeposit(dep_id) {
    var res, response_data;
    dep_id = parseId(dep_id);
    res = requests.post("{}/{}/actions/edit".format(ZENODO_API_URL, dep_id), { "params": params });
    if ((res.status_code !== 201)) {
        console.log("Error in making record editable. {}".format(json.loads(res.content)));
        sys.exit(1);
    }
    response_data = res.json();
    return response_data;
}
function updateRecord(dep_id, metadata) {
    var res, response_data;
    console.log("\tUpdating record.");
    dep_id = parseId(dep_id);
    res = requests.put(((ZENODO_API_URL + "/") + dep_id), { "json": { "metadata": metadata }, "params": params });
    if ((res.status_code !== 200)) {
        console.log("Error in updating record. {}".format(json.loads(res.content)));
        sys.exit(1);
    }
    response_data = res.json();
    return response_data;
}
function fileUpload(bucket_url, journal_filepath) {
    var fp, replaced, res;
    console.log("\tUploading file.");
    fp = open(journal_filepath, "rb");
    replaced = re.sub("^.*\\/", "", journal_filepath);
    res = requests.put(((bucket_url + "/") + replaced), { "data": fp, "params": params });
    fp.close;
    if ((res.status_code !== 200)) {
        sys.exit(json.dumps(res.json()));
    }
    console.log("\tUpload successful.");
}
function duplicate(args) {
    var bucket_url, deposit_url, metadata, response_data;
    metadata = getMetadata(args.id[0]);
    delete metadata["doi"];
    metadata["prereserve_doi"] = true;
    metadata = updateMetadata(args, metadata);
    response_data = createRecord(metadata);
    bucket_url = response_data["links"]["bucket"];
    deposit_url = response_data["links"]["html"];
    if (args.files) {
        for (var filePath, _pj_c = 0, _pj_a = args.files, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            filePath = _pj_a[_pj_c];
            fileUpload(bucket_url, filePath);
        }
    }
    finalActions(args, response_data["id"], deposit_url);
}
function upload(args) {
    var bucket_url, deposit_url, response;
    bucket_url = null;
    if (args.bucketurl) {
        bucket_url = args.bucketurl;
    }
    else {
        if (args.id) {
            response = getData(args.id);
            bucket_url = response["links"]["bucket"];
            deposit_url = response["links"]["html"];
        }
    }
    if (bucket_url) {
        for (var filePath, _pj_c = 0, _pj_a = args.files, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            filePath = _pj_a[_pj_c];
            fileUpload(bucket_url, filePath);
        }
        finalActions(args, args.id, deposit_url);
    }
    else {
        console.log("Unable to upload: id and bucketurl both not specified.");
    }
}
function updateMetadata(args, metadata) {
    var author_data_dict, author_data_fp, author_info, comm, creator, meta_file;
    author_data_dict = {};
    if ((_pj.in_es6("json", args.__dict__) && args.json)) {
        meta_file = open(args.json);
        //for (key, value) in json.load(meta_file).items():                                                                                                                   
        //metadata[key] = value  
        meta_file.close();
    }
    if (_pj.in_es6("creators", metadata)) {
        metadata["authors"] = ";".join(function () {
            var _pj_a = [], _pj_b = metadata["creators"];
            for (var _pj_c = 0, _pj_d = _pj_b.length; (_pj_c < _pj_d); _pj_c += 1) {
                var creator = _pj_b[_pj_c];
                _pj_a.push(creator["name"]);
            }
            return _pj_a;
        }
            .call(this));
    }
    if ((_pj.in_es6("title", args.__dict__) && args.title)) {
        metadata["title"] = args.title;
    }
    if ((_pj.in_es6("date", args.__dict__) && args.date)) {
        metadata["publication_date"] = args.date;
    }
    if ((_pj.in_es6("description", args.__dict__) && args.description)) {
        metadata["description"] = args.description;
    }
    if ((_pj.in_es6("add_communites", args.__dict__) && args.add_communites)) {
        metadata["communities"] = function () {
            var _pj_a = [], _pj_b = args.add_communities;
            for (var _pj_c = 0, _pj_d = _pj_b.length; (_pj_c < _pj_d); _pj_c += 1) {
                var community = _pj_b[_pj_c];
                _pj_a.push({ "identifier": community });
            }
            return _pj_a;
        }
            .call(this);
    }
    if ((_pj.in_es6("remove_communities", args.__dict__) && args.remove_communities)) {
        metadata["communities"] = list(filter(function (comm) {
            return (!_pj.in_es6(comm["identifier"], args.remove_communities));
        }, metadata["communities"]));
    }
    if ((_pj.in_es6("communities", args.__dict__) && args.communities)) {
        comm = open(args.communities);
        metadata["communities"] = function () {
            var _pj_a = [], _pj_b = comm.read().splitlines();
            for (var _pj_c = 0, _pj_d = _pj_b.length; (_pj_c < _pj_d); _pj_c += 1) {
                var community = _pj_b[_pj_c];
                _pj_a.push({ "identifier": community });
            }
            return _pj_a;
        }
            .call(this);
        comm.close();
    }
    if ((_pj.in_es6("authordata", args.__dict__) && args.authordata)) {
        author_data_fp = open(args.authordata);
        for (var author_data, _pj_c = 0, _pj_a = author_data_fp.read().splitlines(), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            author_data = _pj_a[_pj_c];
            if (author_data.strip()) {
                creator = author_data.split("\t");
                author_data_dict["name"] = { "name": creator[0], "affiliation": creator[1], "orcid": creator[2] };
            }
        }
        author_data_fp.close();
    }
    if ((_pj.in_es6("authors", args.__dict__) && args.authors)) {
        metadata["creators"] = [];
        for (var author, _pj_c = 0, _pj_a = args.authors.split(";"), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            author = _pj_a[_pj_c];
            author_info = author_data_dict.get(author, null);
            metadata["creators"].append({ "name": author, "affiliation": (author_info ? author_info["affiliation"] : ""), "orcid": (author_info ? author_info["orcid"] : "") });
        }
    }
    if ((_pj.in_es6("zotero_link", args.__dict__) && args.zotero_link)) {
        metadata["related_identifiers"] = [{ "identifier": args.zotero_link, "relation": "isAlternateIdentifier", "resource_type": "other", "scheme": "url" }];
    }
    return metadata;
}
function update(args) {
    var bucket_url, data, deposit_url, id, metadata, response, response_data;
    id = parseId(args.id[0]);
    data = getData(id);
    metadata = data["metadata"];
    if ((data["state"] === "done")) {
        console.log("\tMaking record editable.");
        response = editDeposit(id);
    }
    metadata = updateMetadata(args, metadata);
    response_data = updateRecord(id, metadata);
    bucket_url = response_data["links"]["bucket"];
    deposit_url = response_data["links"]["html"];
    if (args.files) {
        for (var filePath, _pj_c = 0, _pj_a = args.files, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            filePath = _pj_a[_pj_c];
            fileUpload(bucket_url, filePath);
        }
    }
    finalActions(args, id, deposit_url);
}
function finalActions(args, id, deposit_url) {
    if ((_pj.in_es6("publish", args.__dict__) && args.publish)) {
        publishDeposition(id);
    }
    if ((_pj.in_es6("show", args.__dict__) && args.show)) {
        showDeposition(id);
    }
    if ((_pj.in_es6("dump", args.__dict__) && args.dump)) {
        dumpDeposition(id);
    }
    if ((_pj.in_es6("open", args.__dict__) && args.open)) {
        //webbrowser.open_new_tab(deposit_url);
        opn(deposit_url);
    }
}
function create(args) {
    var f, metadata, response_data;
    f = open("blank.json", { "mode": "r" });
    metadata = json.loads(f.read());
    f.close();
    metadata = updateMetadata(args, metadata);
    response_data = createRecord(metadata);
    finalActions(args, response_data["id"], response_data["links"]["html"]);
}
function copy(args) {
    var bucket_url, metadata, response_data;
    metadata = getMetadata(args.id);
    delete metadata["doi"];
    delete metadata["prereserve_doi"];
    for (var journal_filepath, _pj_c = 0, _pj_a = args.files, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
        journal_filepath = _pj_a[_pj_c];
        console.log(("Processing: " + journal_filepath));
        response_data = createRecord(metadata);
        bucket_url = response_data["links"]["bucket"];
        fileUpload(bucket_url, journal_filepath);
        finalActions(args, response_data["id"], response_data["links"]["html"]);
    }
}
function listDepositions(args) {
    var listParams, res;
    listParams = params;
    listParams["page"] = args.page;
    listParams["size"] = (args.size ? args.size : 1000);
    res = requests.get(ZENODO_API_URL, { "params": listParams });
    if ((res.status_code !== 200)) {
        console.log("Failed in listDepositions: {}".format(json.loads(res.content)));
        sys.exit(1);
    }
    if ((_pj.in_es6("dump", args.__dict__) && args.dump)) {
        dumpJSON(res.json());
    }
    for (var dep, _pj_c = 0, _pj_a = res.json(), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
        dep = _pj_a[_pj_c];
        console.log("{} {}".format(dep["record_id"], dep["conceptrecid"]));
        if ((_pj.in_es6("publish", args.__dict__) && args.publish)) {
            publishDeposition(dep["id"]);
        }
        if ((_pj.in_es6("show", args.__dict__) && args.show)) {
            showDepositionJSON(dep);
        }
        if ((_pj.in_es6("open", args.__dict__) && args.open)) {
            opn(dep["links"]["html"]);
        }
    }
}
function newVersion(args) {
    var bucket_url, deposit_url, id, metadata, newmetadata, response, response_data;
    id = parseId(args.id[0]);
    response = requests.post("{}/{}/actions/newversion".format(ZENODO_API_URL, id), { "params": params });
    if ((response.status_code !== 201)) {
        console.log("New version request failed: {}".format(json.loads(response.content)));
        sys.exit(1);
    }
    response_data = response.json();
    metadata = getMetadata(id);
    newmetadata = updateMetadata(args, metadata);
    if ((newmetadata !== metadata)) {
        response_data = updateRecord(id, newmetadata);
    }
    bucket_url = response_data["links"]["bucket"];
    deposit_url = response_data["links"]["latest_html"];
    if (args.files) {
        for (var filePath, _pj_c = 0, _pj_a = args.files, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            filePath = _pj_a[_pj_c];
            fileUpload(bucket_url, filePath);
        }
    }
    finalActions(args, response_data["id"], deposit_url);
    console.log("latest_draft: ", response_data["links"]["latest_draft"]);
}
function download(args) {
    var contents, data, fp, id, name;
    id = parseId(args.id[0]);
    data = getData(id);
    for (var fileObj, _pj_c = 0, _pj_a = data["files"], _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
        fileObj = _pj_a[_pj_c];
        name = fileObj["filename"];
        console.log("Downloading " + name);
        contents = requests.get(fileObj["links"]["download"], { "params": params });
        fp = open(name, "wb+");
        fp.write(contents.content);
        fp.close();
        fp = open((name + ".md5"), "w+");
        fp.write(((fileObj["checksum"] + " ") + fileObj["filename"]));
        fp.close();
    }
}
function concept(args) {
    var id, listParams, res;
    id = parseId(args.id[0]);
    listParams = params;
    listParams["q"] = ("conceptrecid:" + id);
    res = requests.get(ZENODO_API_URL, { "params": listParams });
    if ((res.status_code !== 200)) {
        console.log("Failed in concept(args): {}".format(json.loads(res.content)));
        sys.exit(1);
    }
    if ((_pj.in_es6("dump", args.__dict__) && args.dump)) {
        dumpJSON(res.json());
    }
    for (var dep, _pj_c = 0, _pj_a = res.json(), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
        dep = _pj_a[_pj_c];
        console.log("{} {}".format(dep["record_id"], dep["conceptrecid"]));
        if ((_pj.in_es6("publish", args.__dict__) && args.publish)) {
            publishDeposition(dep["id"]);
        }
        if ((_pj.in_es6("show", args.__dict__) && args.show)) {
            showDepositionJSON(dep);
        }
        if ((_pj.in_es6("open", args.__dict__) && args.open)) {
            opn(dep["links"]["html"]);
        }
    }
}
parser = new argparse.ArgumentParser({ "description": "Zenodo command line utility" });
parser.add_argument("--config", { "action": "store", "default": "config.json", "help": "Config file with API key. By default config.json then ~/.config/zenodo-cli/config.json are used if no config is provided." });
subparsers = parser.add_subparsers({ "help": "sub-command help" });
parser_list = subparsers.add_parser("list", { "help": "List deposits for this account. Note that the Zenodo API does not seem to send continuation tokens. The first 1000 results are retrieved. Please use --page to retrieve more. The result is the record id, followed by the concept id." });
parser_list.add_argument("--page", { "action": "store", "help": "Page number of the list." });
parser_list.add_argument("--size", { "action": "store", "help": "Number of records in one page." });
parser_list.add_argument("--publish", { "action": "store_true", "help": "Publish the depositions after executing the command.", "default": false });
parser_list.add_argument("--open", { "action": "store_true", "help": "Open the depositions in the browser after executing the command.", "default": false });
parser_list.add_argument("--show", { "action": "store_true", "help": "Show key information for the depositions after executing the command.", "default": false });
parser_list.add_argument("--dump", { "action": "store_true", "help": "Show json for list and for depositions after executing the command.", "default": false });
parser_list.set_defaults({ "func": listDepositions });
parser_get = subparsers.add_parser("get", { "help": "The get command gets the ids listed, and writes these out to id1.json, id2.json etc. The id can be provided as a number, as a deposit URL or record URL" });
parser_get.add_argument("id", { "nargs": "*" });
parser_get.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_get.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_get.add_argument("--show", { "action": "store_true", "help": "Show key information for the deposition after executing the command.", "default": false });
parser_get.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_get.set_defaults({ "func": saveIdsToJson });
parser_create = subparsers.add_parser("create", { "help": "The create command creates new records based on the json files provided, optionally providing a title / date / description / files." });
parser_create.add_argument("--json", { "action": "store", "help": "Path of the JSON file with the metadata for the zenodo record to be created. If this file is not provided, a template is used. The following options override settings from the JSON file / template." });
parser_create.add_argument("--title", { "action": "store", "help": "The title of the record. Overrides data provided via --json." });
parser_create.add_argument("--date", { "action": "store", "help": "The date of the record. Overrides data provided via --json." });
parser_create.add_argument("--description", { "action": "store", "help": "The description (abstract) of the record. Overrides data provided via --json." });
parser_create.add_argument("--communities", { "action": "store", "help": "List of communities for the record (comma-separated). Overrides data provided via --json." });
parser_create.add_argument("--add-communities", { "nargs": "*" });
parser_create.add_argument("--authors", { "action": "store", "help": "List of authors, separated with semicolon. Do not provide institution/ORCID. Instead, these can be supplied using --authordata. Overrides data provided via --json." });
parser_create.add_argument("--authordata", { "action": "store", "help": "A text file with a database of authors. Each line has author, institution, ORCID (tab-separated). The data is used to supplement insitution/ORCID to author names specified with --authors. Note that authors are only added to the record when specified with --authors, not because they appear in the specified authordate file. " });
parser_create.add_argument("--zotero-link", { "action": "store", "help": "Zotero link of the zotero record to be linked. Overrides data provided via --json." });
parser_create.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_create.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_create.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_create.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_create.set_defaults({ "func": create });
parser_duplicate = subparsers.add_parser("duplicate", { "help": "The duplicate command duplicates the id to a new id, optionally providing a title / date / description / files." });
parser_duplicate.add_argument("id", { "nargs": 1 });
parser_duplicate.add_argument("--title", { "action": "store" });
parser_duplicate.add_argument("--date", { "action": "store" });
parser_duplicate.add_argument("--files", { "nargs": "*" });
parser_duplicate.add_argument("--description", { "action": "store" });
parser_duplicate.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_duplicate.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_duplicate.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_duplicate.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_duplicate.set_defaults({ "func": duplicate });
parser_update = subparsers.add_parser("update", { "help": "The update command updates the id provided, with the title / date / description / files provided." });
parser_update.add_argument("id", { "nargs": 1 });
parser_update.add_argument("--title", { "action": "store" });
parser_update.add_argument("--date", { "action": "store" });
parser_update.add_argument("--description", { "action": "store" });
parser_update.add_argument("--files", { "nargs": "*" });
parser_update.add_argument("--add-communities", { "nargs": "*" });
parser_update.add_argument("--remove-communities", { "nargs": "*" });
parser_update.add_argument("--zotero-link", { "action": "store", "help": "Zotero link of the zotero record to be linked." });
parser_update.add_argument("--json", { "action": "store", "help": "Path of the JSON file with the metadata of the zenodo record to be updated." });
parser_update.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_update.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_update.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_update.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_update.set_defaults({ "func": update });
parser_upload = subparsers.add_parser("upload", { "help": "Just upload files (shorthand for update id --files ...)" });
parser_upload.add_argument("id", { "nargs": "?" });
parser_upload.add_argument("--bucketurl", { "action": "store" });
parser_upload.add_argument("files", { "nargs": "*" });
parser_upload.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_upload.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_upload.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_upload.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_upload.set_defaults({ "func": upload });
parser_copy = subparsers.add_parser("multiduplicate", { "help": "Duplicates existing deposit with id multiple times, once for each file." });
parser_copy.add_argument("id", { "nargs": 1 });
parser_copy.add_argument("files", { "nargs": "*" });
parser_copy.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_copy.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_copy.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_copy.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_copy.set_defaults({ "func": copy });
parser_newversion = subparsers.add_parser("newversion", { "help": "The newversion command creates a new version of the deposition with id, optionally providing a title / date / description / files." });
parser_newversion.add_argument("id", { "nargs": 1 });
parser_newversion.add_argument("--title", { "action": "store" });
parser_newversion.add_argument("--date", { "action": "store" });
parser_newversion.add_argument("--files", { "nargs": "*" });
parser_newversion.add_argument("--description", { "action": "store" });
parser_newversion.add_argument("--publish", { "action": "store_true", "help": "Publish the deposition after executing the command.", "default": false });
parser_newversion.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_newversion.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_newversion.add_argument("--dump", { "action": "store_true", "help": "Show json for deposition after executing the command.", "default": false });
parser_newversion.set_defaults({ "func": newVersion });
parser_download = subparsers.add_parser("download", { "help": "Download all the files in the deposition." });
parser_download.add_argument("id", { "nargs": 1 });
parser_download.set_defaults({ "func": download });
parser_concept = subparsers.add_parser("concept", { "help": "Get the record id from a concept id." });
parser_concept.add_argument("id", { "nargs": 1 });
parser_concept.add_argument("--dump", { "action": "store_true", "help": "Show json for list and for depositions after executing the command.", "default": false });
parser_concept.add_argument("--open", { "action": "store_true", "help": "Open the deposition in the browser after executing the command.", "default": false });
parser_concept.add_argument("--show", { "action": "store_true", "help": "Show the info of the deposition after executing the command.", "default": false });
parser_concept.set_defaults({ "func": concept });
args = parser.parse_args();
if ((process.argv.length === 1)) {
    parser.print_help(sys.stderr);
    sys.exit(1);
}
loadConfig(args.config);
args.func(args);
//# sourceMappingURL=zenodo-cli-2.js.map

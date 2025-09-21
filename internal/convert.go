package internal

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"os"
	"reflect"
	"strconv"
	"strings"

	"bchmnn/poodle-cli/internal/util"

	"github.com/swaggest/jsonschema-go"
	"github.com/swaggest/openapi-go/openapi31"
)

type Converter struct {
	Moodle            *util.Moodle
	Input             string
	OutPath           string
	BlacklistPath     string
	WhitelistPath     string
	AddLoginTokenPath bool
	FixActivityBadge  bool
	FixDefaults       bool
	AddTags           bool
	UsePrettier       bool
	ToStdout          bool
	LogWriter         io.Writer
	Log               *log.Logger
}

func NewConverter(moodle *util.Moodle, input string, outPath string, blacklistPath string, whitelistPath string, addLoginTokenPath bool, fixActivityBadge bool, fixDefaults bool, addTags bool, usePrettier bool, toStdout bool) *Converter {
	var logWriter io.Writer
	if toStdout {
		logWriter = os.Stderr
	} else {
		logWriter = os.Stdout
	}

	return &Converter{
		Moodle:            moodle,
		Input:             input,
		OutPath:           outPath,
		BlacklistPath:     blacklistPath,
		WhitelistPath:     whitelistPath,
		AddLoginTokenPath: addLoginTokenPath,
		FixActivityBadge:  fixActivityBadge,
		FixDefaults:       fixDefaults,
		AddTags:           addTags,
		UsePrettier:       usePrettier,
		ToStdout:          toStdout,
		LogWriter:         logWriter,
		Log:               log.New(logWriter, "[CONVERTER] ", log.LstdFlags),
	}
}

type Resp struct {
	jsonschema.Struct
	jsonschema.Schema
}

type Req Resp

type Query struct {
	Args jsonschema.Schema `query:"args"`
}

func (p *Converter) Convert() error {
	p.Log.Println("Starting convertion of " + p.Input + " ...")

	spec := openapi31.Spec{
		Openapi: "3.1.0",
		Info: openapi31.Info{
			Title:       "Moodle Webservice API",
			Version:     p.Moodle.Release,
			Description: util.StringPtr("Auto-generated OpenAPI spec for Moodle's Webservice API."),
		},
		Servers: []openapi31.Server{
			{
				URL:         "{scheme}://{host}",
				Description: util.StringPtr("Custom Moodle server URL"),
				Variables: map[string]openapi31.ServerVariable{
					"scheme": {
						Enum:    []string{"http", "https"},
						Default: "https",
					},
					"host": {
						Default:     "localhost",
						Description: util.StringPtr("The hostname of the Moodle server"),
					},
				},
			},
		},
	}
	spec.Components = &openapi31.Components{
		SecuritySchemes: map[string]openapi31.SecuritySchemeOrReference{
			"wstoken": {
				SecurityScheme: &openapi31.SecurityScheme{
					Description: util.StringPtr(
						"Webservice token",
					),
					APIKey: &openapi31.SecuritySchemeAPIKey{
						Name: "wstoken",
						In:   "query",
					},
				},
			},
		},
	}

	methods, err := util.LoadMethods(p.Input)
	if err != nil {
		return err
	}

	if p.BlacklistPath != "" {
		p.Log.Println("Applying blacklist: " + p.BlacklistPath + " ...")
		blacklist, err := util.FileGetLines(p.BlacklistPath)
		if err != nil {
			return err
		}
		filterMethodsBlacklist(methods, blacklist)
	}

	if p.WhitelistPath != "" {
		p.Log.Println("Applying whitelist: " + p.WhitelistPath + " ...")
		whitelist, err := util.FileGetLines(p.WhitelistPath)
		if err != nil {
			return err
		}
		methods = filterMethodsWhitelist(methods, whitelist)
	}

	if p.FixActivityBadge {
		p.Log.Println("Applying Activitybadge fix ...")
		fixActivityBadge(methods)
	}

	p.Log.Printf("Converting (fixing defaults: %v, adding tags: %v) ...", p.FixDefaults, p.AddTags)
	mapOfPathItemValues := make(map[string]openapi31.PathItem)
	if p.AddLoginTokenPath {
		p.Log.Println("Adding login token path ...")
		stringType := jsonschema.String.Type()
		stringSchema := jsonschema.SchemaOrBool{
			TypeObject: &jsonschema.Schema{
				Type: &stringType,
			},
		}
		requestSchema := jsonschema.Schema{}
		requestSchema.WithType(jsonschema.Object.Type())
		requestSchema.WithPropertiesItem("username", stringSchema)
		requestSchema.WithPropertiesItem("password", stringSchema)
		requestSchema.WithPropertiesItem("service", stringSchema)
		requestSchema.WithRequired("username", "password", "service")
		requestSchemaSm, _ := requestSchema.ToSchemaOrBool().ToSimpleMap()
		requestBody := openapi31.RequestBody{}
		requestBody.WithRequired(true)
		requestBody.WithContent(map[string]openapi31.MediaType{
			"application/x-www-form-urlencoded": {
				Schema: requestSchemaSm,
			},
		})
		responseSchema := jsonschema.Schema{}
		responseSchema.WithType(jsonschema.Object.Type())
		responseSchema.WithPropertiesItem("token", stringSchema)
		responseSchema.WithPropertiesItem("privatetoken", stringSchema)
		responseSchema.WithRequired("token", "privatetoken")
		responseSchemaSm, _ := responseSchema.ToSchemaOrBool().ToSimpleMap()
		response := openapi31.Response{
			Content: map[string]openapi31.MediaType{
				"application/json": {
					Schema: responseSchemaSm,
				},
			},
		}
		operation := openapi31.Operation{}
		operation.WithID("login_token")
		operation.WithRequestBody(openapi31.RequestBodyOrReference{
			RequestBody: &requestBody,
		})
		operation.WithResponses(openapi31.Responses{
			MapOfResponseOrReferenceValues: map[string]openapi31.ResponseOrReference{
				"200": {
					Response: &response,
				},
			},
		})
		pathItem := openapi31.PathItem{}
		pathItem.WithPost(operation)
		mapOfPathItemValues["/login/token.php"] = pathItem
	}

	for name, method := range methods {
		if !method.LoginRequired && !method.AllowedFromAjax {
			return fmt.Errorf("method %s does not require login and is not allowed from ajax", name)
		}

		respDesc := method.ReturnsDesc.Desc
		if respDesc == "" {
			respDesc = "Successful response"
		}

		operation := openapi31.Operation{
			ID:          &name,
			Summary:     util.OptionalString(method.Description),
			Description: util.OptionalString(method.Description),
		}

		if p.AddTags {
			operation.WithTags(method.Component)
		}

		if method.LoginRequired {
			operation.WithSecurity(map[string][]string{"wstoken": {}})
		}

		paramsSchema := parseDynamicContentToSchema(method.ParametersDesc, p.FixDefaults)
		params, _ := paramsSchema.ToSchemaOrBool().ToSimpleMap()
		id := util.SnakeToPascal(name) + "Parameters"
		ref := "#/components/schemas/" + id
		spec.Components.WithSchemasItem(id, params)
		schemaRef := jsonschema.Schema{Ref: &ref}
		schemaRefSm, _ := schemaRef.ToSchemaOrBool().ToSimpleMap()

		if !method.LoginRequired && len(paramsSchema.Properties) > 0 {
			operation.WithParameters(openapi31.ParameterOrReference{
				Parameter: &openapi31.Parameter{
					In:          openapi31.ParameterInQuery,
					Name:        "args",
					Required:    util.BoolPtr(true),
					Description: util.OptionalString(method.ParametersDesc.Desc),
					Schema:      schemaRefSm,
				},
			})
		}
		if method.LoginRequired && len(paramsSchema.Properties) > 0 {
			operation.WithRequestBody(openapi31.RequestBodyOrReference{
				RequestBody: &openapi31.RequestBody{
					Required:    util.BoolPtr(true),
					Description: util.OptionalString(method.ParametersDesc.Desc),
					Content: map[string]openapi31.MediaType{
						"application/x-www-form-urlencoded": {
							Schema: schemaRefSm,
						},
					},
				},
			})
		}

		params, _ = parseDynamicContentToSchema(method.ReturnsDesc, p.FixDefaults).ToSchemaOrBool().ToSimpleMap()
		id = util.SnakeToPascal(name) + "Response"
		ref = "#/components/schemas/" + id
		spec.Components.WithSchemasItem(id, params)
		schemaRef = jsonschema.Schema{Ref: &ref}
		schemaRefSm, _ = schemaRef.ToSchemaOrBool().ToSimpleMap()

		operation.WithResponses(openapi31.Responses{
			MapOfResponseOrReferenceValues: map[string]openapi31.ResponseOrReference{
				"200": {
					Response: &openapi31.Response{
						Description: method.ReturnsDesc.Desc,
						Content: map[string]openapi31.MediaType{
							"application/json": {
								Schema: schemaRefSm,
							},
						},
					},
				},
			},
		})

		if method.LoginRequired {
			mapOfPathItemValues["/webservice/rest/server.php#"+name] = openapi31.PathItem{
				Post: &operation,
			}
		} else {
			mapOfPathItemValues["/lib/ajax/service-nologin.php#"+name] = openapi31.PathItem{
				Get: &operation,
			}
		}
	}

	spec.WithPaths(openapi31.Paths{
		MapOfPathItemValues: mapOfPathItemValues,
	})

	var result []byte
	var parser string
	if p.ToStdout || strings.HasSuffix(p.OutPath, "json") {
		result, err = spec.MarshalJSON()
		parser = "json"
	} else {
		result, err = spec.MarshalYAML()
		parser = "yaml"
	}
	if err != nil {
		return err
	}

	if p.UsePrettier {
		if util.HasExec("prettier") {
			p.Log.Println("Formatting with prettier ...")
			process := util.Process{
				Name: "prettier",
				Arg: []string{
					"--parser",
					parser,
				},
				Stdin: bytes.NewReader(result), // io.Reader, get result into here,
			}
			p.Log.Println("Running:", process.String())
			result, err = process.Output()
			if err != nil {
				return err
			}
		} else {
			p.Log.Println("prettier not in PATH. Skipping ...")
		}
	}

	writer := os.Stdout
	if !p.ToStdout {
		writer, err = os.Create(p.OutPath)
		if err != nil {
			return fmt.Errorf("Could not create file %s", p.OutPath)
		}
		defer writer.Close()
	}

	_, err = writer.Write(result)

	if !p.ToStdout {
		p.Log.Println("Results written to", p.OutPath)
	}
	return err
}

func parseSchemaType(vartype string) jsonschema.SimpleType {
	switch vartype {
	case "object":
		return jsonschema.Object
	case "":
		return jsonschema.Object
	case "array":
		return jsonschema.Array
	case "string":
		return jsonschema.String
	case "int":
		return jsonschema.Integer
	case "integer":
		return jsonschema.Integer
	case "bool":
		return jsonschema.Boolean
	case "boolean":
		return jsonschema.Boolean
	case "raw":
		return jsonschema.String
	case "alphanum":
		return jsonschema.String
	case "float":
		return jsonschema.Number
	case "number":
		return jsonschema.Number
	case "alphanumext":
		return jsonschema.String
	case "notags":
		return jsonschema.String
	default:
		return jsonschema.String
	}
}

func getDefault(cls jsonschema.SimpleType) any {
	switch cls {
	case jsonschema.Object:
		return make(map[string]any)
	case jsonschema.Array:
		return make([]any, 0)
	case jsonschema.String:
		return ""
	case jsonschema.Integer:
		return 0
	case jsonschema.Number:
		return 0.0
	case jsonschema.Boolean:
		return false
	case jsonschema.Null:
		return nil
	}
	return nil
}

func fixDefault(value any, cls jsonschema.SimpleType, allowNull bool) any {
	if !allowNull && value == nil {
		return getDefault(cls)
	}
	if allowNull && value == nil {
		return value
	}
	v := reflect.ValueOf(value)
	kind := reflect.TypeOf(value).Kind()
	switch cls {
	case jsonschema.Object:
		if kind == reflect.Map || kind == reflect.Struct {
			return value
		}
	case jsonschema.Array:
		if kind == reflect.Array || kind == reflect.Slice {
			return value
		}
	case jsonschema.String:
		if kind == reflect.String {
			return value
		}
		if kind >= reflect.Int && kind <= reflect.Uint64 {
			return fmt.Sprintf("%d", v.Int())
		}
		if kind == reflect.Float32 || kind == reflect.Float64 {
			return fmt.Sprintf("%f", v.Float())
		}
		if kind == reflect.Bool {
			return strconv.FormatBool(v.Bool())
		}
		// if any kind of number or bool convert to string
	case jsonschema.Integer:
		switch kind {
		case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
			return v.Int()
		case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
			return int64(v.Uint())
		case reflect.Bool:
			if v.Bool() {
				return int64(1)
			}
			return int64(0)
		case reflect.String:
			if i, err := strconv.ParseInt(v.String(), 10, 64); err == nil {
				return i
			}
		}
	case jsonschema.Number:
		switch kind {
		case reflect.Float32, reflect.Float64:
			return v.Float()
		case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
			return float64(v.Int())
		case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
			return float64(v.Uint())
		case reflect.String:
			if f, err := strconv.ParseFloat(v.String(), 64); err == nil {
				return f
			}
		case reflect.Bool:
			if v.Bool() {
				return float64(1)
			}
			return float64(0)
		}
		if kind == reflect.Float32 || kind == reflect.Float64 {
			return value
		}
	case jsonschema.Boolean:
		if kind == reflect.Bool {
			return v.Bool()
		}
		switch kind {
		case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
			return v.Int() != 0
		case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
			return v.Uint() != 0
		case reflect.Float32, reflect.Float64:
			return v.Float() != 0
		case reflect.String:
			if b, err := strconv.ParseBool(v.String()); err == nil {
				return b
			}
			if i, err := strconv.Atoi(v.String()); err == nil {
				return i != 0
			}
		}
	}
	return getDefault(cls)
}

func parseDynamicContentToSchema(desc util.DynamicContent, fixDefaults bool) *jsonschema.Schema {
	required := make([]string, 0)

	schema := &jsonschema.Schema{}
	schema.Description = util.OptionalString(desc.Desc)

	if desc.OneOf != nil {
		var oneOfTypes []jsonschema.SchemaOrBool
		for _, content := range desc.OneOf {
			oneOfTypes = append(oneOfTypes, parseDynamicContentToSchema(*content, fixDefaults).ToSchemaOrBool())
		}
		schema.WithOneOf(oneOfTypes...)
		return schema
	}

	var schemaType jsonschema.SimpleType
	if desc.Content != nil {
		// it's an array
		schemaType = jsonschema.Array
		itemSchema := parseDynamicContentToSchema(*desc.Content, fixDefaults)
		items := jsonschema.Items{}
		items.WithSchemaOrBool(itemSchema.ToSchemaOrBool())
		schema.WithItems(items)
	} else if desc.Keys != nil {
		// it's an object
		schemaType = jsonschema.Object
		for key, value := range desc.Keys {
			if value.Required == 1 {
				required = append(required, key)
			}
			schema.WithPropertiesItem(key, jsonschema.SchemaOrBool{
				TypeObject: parseDynamicContentToSchema(*value, fixDefaults),
			})
		}
	} else {
		schemaType = parseSchemaType(desc.Type)
	}

	if desc.AllowNull {
		schema.WithType(jsonschema.Type{
			SliceOfSimpleTypeValues: []jsonschema.SimpleType{
				jsonschema.Null,
				schemaType,
			},
		})
	} else {
		schema.AddType(schemaType)
	}

	if fixDefaults {
		schema.WithDefault(fixDefault(desc.Default, schemaType, desc.AllowNull))
	} else {
		schema.WithDefault(desc.Default)
	}

	schema.Required = required

	return schema
}

func filterMethodsBlacklist(methods util.Methods, blacklist []string) {
	for _, entry := range blacklist {
		delete(methods, entry)
	}
}

func filterMethodsWhitelist(methods util.Methods, whitelist []string) util.Methods {
	tmp := make(util.Methods)
	for _, entry := range whitelist {
		if method, ok := methods[entry]; ok {
			tmp[entry] = method
		}
	}
	return tmp
}

// Activitybadge is meant to be an object.
// However, if there is no Activitybadge, the moodle server returns an
// empty list.
// Therefore, Activitybadge is fixed to be "OneOf": object, or list.
func fixActivityBadge(methods util.Methods) {

	method, ok := methods["core_course_get_contents"]
	if !ok {
		return
	}

	if method.ReturnsDesc.Content == nil || method.ReturnsDesc.Content.Keys == nil {
		return
	}
	keys := method.ReturnsDesc.Content.Keys

	modules, ok := keys["modules"]
	if !ok {
		return
	}

	if modules.Content == nil || modules.Content.Keys == nil {
		return
	}

	parentKeys := modules.Content.Keys

	activityBadge, ok := parentKeys["activitybadge"]
	if !ok {
		return
	}

	parentKeys["activitybadge"] = &util.DynamicContent{
		OneOf: []*util.DynamicContent{
			// as object
			activityBadge,
			// as list
			{
				Content: activityBadge,
				Description: util.Description{
					AllowNull: activityBadge.AllowNull,
					Default:   []any{},
					Desc:      activityBadge.Desc,
					Required:  activityBadge.Required,
				},
			},
		},
	}
}

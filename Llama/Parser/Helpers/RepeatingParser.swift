//
//  RepeatingParser.swift
//  Llama
//
//  Created by Mathias Quintero on 24.02.19.
//  Copyright © 2019 Mathias Quintero. All rights reserved.
//

import Foundation

postfix operator *
postfix operator +

postfix func * <P: Parser>(_ p: P) -> AnyParser<[P.Output]> {
    return RepeatingParser(source: p).any()
}

postfix func + <P: Parser>(_ p: P) -> AnyParser<[P.Output]> {
    let parser = p && p*
    return parser.map { [$0] + $1 }
}

private struct RepeatingParser<Source: Parser>: Parser {
    typealias Output = [Source.Output]
    let source: Source
    
    func parse(tokens: [Token]) throws -> ParserOutput<[Source.Output]> {
        let current: ParserOutput<Source.Output>
        do {
            current = try source.parse(tokens: tokens)
        } catch {
            return ParserOutput(output: [], remaining: tokens)
        }
        
        let remaining = try parse(tokens: current.remaining)
        return remaining.map { [current.output] + $0 }
    }
}
